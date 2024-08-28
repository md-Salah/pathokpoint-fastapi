from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete
from typing import Sequence
from uuid import UUID
import os
import logging
import tempfile
import aiofiles
from typing import Tuple, List

from app.models import Image, User, Book, Author, Category, Publisher, Review, PaymentGateway
from app.controller.exception import NotFoundException, ServerErrorException, BadRequestException
from app.library.cloudinary import upload_file_to_cloudinary, delete_file_from_cloudinary, update_file
from app.constant.image import ImageFolder
from app.library.img_resize import img_resize

logger = logging.getLogger(__name__)


async def get_image_by_id(id: UUID, db: AsyncSession) -> Image:
    image = await db.get(Image, id)
    if not image:
        raise NotFoundException('Image not found', str(id))
    return image


async def get_all_images(page: int, per_page: int, db: AsyncSession) -> Sequence[Image]:
    offset = (page - 1) * per_page
    result = await db.execute(select(Image).offset(offset).limit(per_page))
    return result.scalars().all()


async def count_image(db: AsyncSession) -> int:
    result = await db.execute(select(func.count()).select_from(Image))
    return result.scalar_one()


async def read_file(file: UploadFile, MAX_MB: int = 2) -> str:
    CHUNK_SIZE = 1 * 1024 * 1024

    if file.size is None:
        raise BadRequestException('File size is unknown')
    elif file.size > MAX_MB * CHUNK_SIZE:
        raise BadRequestException('File size should not exceed {}MB'.format(MAX_MB))

    try:
        tmp_dir = 'dummy/tmp'
        if not os.path.exists(tmp_dir):
            os.makedirs(tmp_dir)
        with tempfile.NamedTemporaryFile(dir=tmp_dir, delete=False) as temp_file:
            tmp_file = temp_file.name
            async with aiofiles.open(tmp_file, 'wb') as f:
                while chunk := await file.read(CHUNK_SIZE):
                    await f.write(chunk)
            return tmp_file
    except Exception as err:
        logger.error(f'Error while uploading image: {err}')
        raise ServerErrorException('Error while uploading image')


async def create_image(file: UploadFile, folder: ImageFolder, dimension: Tuple[int, int], max_kb: int, db: AsyncSession, optimizer: bool = True) -> Image:
    tmp_file = await read_file(file)
    if optimizer:
        await img_resize(tmp_file, dimension, max_kb)

    response = await upload_file_to_cloudinary(tmp_file, filename=file.filename, folder=folder.value)
    os.remove(tmp_file)
    if not response:
        raise ServerErrorException('Image upload failed')

    image = Image(name=response['filename'],
                  src=response['secure_url'], public_id=response['public_id'], folder=folder)
    db.add(image)
    return image


async def inventory_img_uploader(files: list[UploadFile], db: AsyncSession, **kwargs) -> Sequence[Image]:
    if kwargs.get('book_id'):
        book = await db.get(Book, kwargs['book_id'])
        if not book:
            raise NotFoundException('Book not found', str(kwargs['book_id']))
        dimension, max_kb = (260, 372), 20

        _ = await book.awaitable_attrs.images
        if kwargs['is_append']:
            [book.images.append(
                await create_image(file, ImageFolder.book, dimension, max_kb, db)
            )
                for file in files]
        else:
            book.images = [await create_image(file, ImageFolder.book, dimension, max_kb, db)
                           for file in files]

        await db.commit()
        return book.images

    elif kwargs.get('author_id'):
        author = await db.get(Author, kwargs['author_id'])
        if not author:
            raise NotFoundException(
                'Author not found', str(kwargs['author_id']))

        if kwargs['is_cover_photo']:
            dimension, max_kb = (1328, 256), 20
            _ = await author.awaitable_attrs.banner
            author.banner = await create_image(files[0], ImageFolder.author, dimension, max_kb, db)

            await db.commit()
            return [author.banner]
        else:
            dimension, max_kb = (120, 120), 10
            _ = await author.awaitable_attrs.image
            author.image = await create_image(files[0], ImageFolder.author, dimension, max_kb, db)

            await db.commit()
            return [author.image]

    elif kwargs.get('category_id'):
        category = await db.get(Category, kwargs['category_id'])
        if not category:
            raise NotFoundException(
                'Category not found', str(kwargs['category_id']))

        if kwargs['is_cover_photo']:
            dimension, max_kb = (1328, 256), 20
            _ = await category.awaitable_attrs.banner
            category.banner = await create_image(files[0], ImageFolder.category, dimension, max_kb, db)

            await db.commit()
            return [category.banner]
        else:
            dimension, max_kb = (237, 181), 10
            _ = await category.awaitable_attrs.image
            category.image = await create_image(files[0], ImageFolder.category, dimension, max_kb, db)

            await db.commit()
            return [category.image]

    elif kwargs.get('publisher_id'):
        publisher = await db.get(Publisher, kwargs['publisher_id'])
        if not publisher:
            raise NotFoundException(
                'Publisher not found', str(kwargs['publisher_id']))

        if kwargs['is_cover_photo']:
            dimension, max_kb = (1328, 256), 20
            _ = await publisher.awaitable_attrs.banner
            publisher.banner = await create_image(files[0], ImageFolder.publisher, dimension, max_kb, db)

            await db.commit()
            return [publisher.banner]
        else:
            dimension, max_kb = (187, 133), 10
            _ = await publisher.awaitable_attrs.image
            publisher.image = await create_image(files[0], ImageFolder.publisher, dimension, max_kb, db)

            await db.commit()
            return [publisher.image]
    
    elif kwargs.get('payment_gateway_id'):
        payment_gateway = await db.get(PaymentGateway, kwargs['payment_gateway_id'])
        if not payment_gateway:
            raise NotFoundException(
                'Payment Gateway not found', str(kwargs['payment_gateway_id']))

        dimension, max_kb = (64, 40), 5
        _ = await payment_gateway.awaitable_attrs.image
        payment_gateway.image = await create_image(files[0], ImageFolder.payment_gateway, 
                                                   dimension, max_kb, db, kwargs.get('optimizer', True))

        await db.commit()
        return [payment_gateway.image]
    
    else:
        raise BadRequestException(
            'book_id, author_id, category_id, publisher_id or payment_gateway_id is required')


async def customer_img_uploader(files: list[UploadFile], user_id: UUID, db: AsyncSession, **kwargs) -> Sequence[Image]:
    if kwargs.get('review_id') and kwargs.get('is_profile_pic'):
        raise BadRequestException(
            'review_id and is_profile_pic cannot be used together')

    user = await db.get(User, user_id)
    if not user:
        raise NotFoundException('User not found', str(user_id))

    if kwargs.get('is_profile_pic'):
        dimension, max_kb = (120, 120), 10
        _ = await user.awaitable_attrs.image
        user.image = await create_image(files[0], ImageFolder.profile_picture, dimension, max_kb, db)

        await db.commit()
        return [user.image]

    elif kwargs.get('review_id'):
        review = await db.get(Review, kwargs['review_id'])
        if not review:
            raise NotFoundException(
                'Review not found', str(kwargs['review_id']))
        if review.user_id != user_id:
            raise BadRequestException(
                'You are not authorized to update this review')
        _ = await review.awaitable_attrs.images
        review.images = [await create_image(file, ImageFolder.review, (260, 372), 20, db) for file in files]

        await db.commit()
        return review.images
    else:
        raise BadRequestException('review_id or is_profile_pic is required')


# async def update_image(id: UUID, file: UploadFile, filename: str | None, alt: str, db: AsyncSession) -> Image:
#     image = await db.get(Image, id)
#     if not image:
#         raise NotFoundException('Image not found', str(id))

#     tmp_file = await read_file(file)
#     await img_resize(tmp_file, (260, 372), 20)
#     filename = filename or file.filename or ""

#     response = await update_file(tmp_file, public_id=image.public_id, filename=filename)
#     os.remove(tmp_file)
#     if not response:
#         raise ServerErrorException('Image upload failed')

#     image.public_id = response['public_id']
#     image.src = response['secure_url']
#     image.name = filename
#     await db.commit()
#     return image


async def delete_image(id: UUID, db: AsyncSession) -> None:
    image = await get_image_by_id(id, db)
    success = await delete_file_from_cloudinary(image.public_id)
    if not success:
        raise ServerErrorException('Image delete failed')
    await db.delete(image)
    await db.commit()


async def delete_image_bulk(ids: Sequence[UUID], db: AsyncSession) -> None:
    images = (await db.scalars(select(Image).filter(Image.id.in_(ids)))).all()

    for image in images:
        success = await delete_file_from_cloudinary(image.public_id)
        if not success:
            raise ServerErrorException('Image delete failed')

    await db.execute(delete(Image).where(Image.id.in_(ids)))
    await db.commit()


async def validate_img(id: UUID | None, db: AsyncSession) -> Image | None:
    if id:
        img = await db.get(Image, id)
        if not img:
            raise NotFoundException('Image not found', str(id))
        return img
    return None


async def validate_imgs(ids: List[UUID], db: AsyncSession) -> Sequence[Image]:
    if not ids:
        return []
    imgs = (await db.scalars(select(Image).filter(Image.id.in_(ids)))).all()
    missing_ids = [id for id in ids if id not in [img.id for img in imgs]]
    if missing_ids:
        raise NotFoundException('Image not found', ','.join(
            str(id) for id in missing_ids))
    return imgs
