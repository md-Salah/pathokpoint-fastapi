import logging
from io import BufferedReader
import traceback
import aioboto3
import mimetypes
from botocore.exceptions import ClientError

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


from app.config.settings import settings

logger = logging.getLogger(__name__)


async def upload_file(file: BufferedReader | bytes, filename: str, folder: str) -> str | None:
    try:
        session = aioboto3.Session(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )

        content_type, _ = mimetypes.guess_type(filename)

        async with session.client('s3') as s3:  # type: ignore
            key = f"{folder}/{filename}"
            await s3.put_object(
                Bucket=settings.BUCKET_NAME,
                Key=key,
                Body=file,
                ContentType=content_type,
                ACL='public-read'  # Set ACL to public-read
            )
            logger.info(
                "File '{}' uploaded successfully to '{}'".format(filename, folder))

            return key

    except ClientError:
        logger.error(f"Failed to upload file: {traceback.format_exc()}")


async def delete_file(filename: str, folder: str) -> bool:
    try:
        session = aioboto3.Session(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        async with session.client('s3') as s3:  # type: ignore
            key = f"{folder}/{filename}"
            await s3.delete_object(Bucket=settings.BUCKET_NAME, Key=key)
        return True
    except ClientError:
        logger.error(f"Failed to delete file: {traceback.format_exc()}")
        return False


def public_url(filename: str, folder: str) -> str:
    key = f"{folder}/{filename}"
    return f"https://{settings.BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/{key}"


async def signed_url(filename: str, folder: str, expires_in: int = 3600):
    try:
        session = aioboto3.Session(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        async with session.client('s3') as s3:  # type: ignore
            key = f"{folder}/{filename}"
            url = await s3.generate_presigned_url(
                'get_object',
                Params={'Bucket': settings.BUCKET_NAME, 'Key': key},
                ExpiresIn=expires_in
            )
            return url
    except ClientError:
        logger.error("Failed to generate signed URL: {}".format(
            traceback.format_exc()))


async def attach_s3_imgs_with_books(db: AsyncSession) -> bool:
    from app.models import Book, Image
    folder = 'book'
    not_found = []
    try:
        session = aioboto3.Session(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        async with session.client('s3') as s3:  # type: ignore
            paginator = s3.get_paginator('list_objects_v2')
            async for page in paginator.paginate(Bucket=settings.BUCKET_NAME, Prefix=folder):
                objs = page.get('Contents', [])
                logger.info(
                    'Attaching Images. Number of objects: {}'.format(len(objs)-1))
                count = {
                    'attached': 0,
                    'already_attached': 0,
                    'object_deleted': 0
                }

                for obj in objs:
                    if obj['Key'] == folder + '/':
                        continue
                    key = obj['Key']
                    logger.debug('Key: {}'.format(key))
                    try:
                        filename = key.split('/')[-1]
                        sku = key.split('/')[-1].split('.')[0]
                        book = await db.scalar(select(Book).filter(Book.sku == sku))
                        logger.debug(book)
                        if book:
                            logger.debug(book.images)
                            for img in book.images:
                                if img.name == filename:
                                    count['already_attached'] += 1
                                    break
                            else:
                                image = Image(name=filename,
                                              src='', public_id='', folder=folder)
                                db.add(image)
                                book.images = [image]
                                await db.commit()
                                logger.debug('Image attached to book')
                                count['attached'] += 1
                        else:
                            count['object_deleted'] += 1
                            # await delete_file(filename, folder)
                            not_found.append(filename)
                    except Exception:
                        logger.error(traceback.format_exc())
                logger.info('Count: {}'.format(count))
                logger.info(
                    'Book not found for the images: {}'.format(not_found))
        return True
    except Exception:
        logger.error(traceback.format_exc())
        return False
