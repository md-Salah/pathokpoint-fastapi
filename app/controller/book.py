from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, distinct
from uuid import UUID
from typing import Sequence
from sqlalchemy.orm import selectinload
import logging
from slugify import slugify
import traceback
import pandas as pd


from app.filter_schema.book import BookFilter, BookFilterMinimal
from app.models import Book, Author, Category, Image, Publisher, Tag
from app.models.book import book_image_link
from app.controller.exception import NotFoundException, ConflictException, ServerErrorException
from app.controller.image import handle_multiple_image_attachment

logger = logging.getLogger(__name__)


query_selectinload = select(Book).options(
    selectinload(Book.publisher),
    selectinload(Book.authors),
    selectinload(Book.translators),
    selectinload(Book.categories),
    selectinload(Book.images),
    selectinload(Book.tags)
)


async def get_book_by_id(id: UUID, db: AsyncSession) -> Book:
    book = await db.scalar(query_selectinload.where(Book.id == id))
    if not book:
        raise NotFoundException('Book not found')
    return book


async def get_all_books(filter: BookFilter, page: int, per_page: int, db: AsyncSession) -> Sequence[Book]:
    offset = (page - 1) * per_page
    query = select(Book).distinct().outerjoin(
        Book.publisher).outerjoin(
        Book.categories).outerjoin(
        Book.authors).outerjoin(
        Book.tags).options(
        selectinload(Book.publisher),
        selectinload(Book.categories),
        selectinload(Book.authors),
        selectinload(Book.translators),
        selectinload(Book.images),
        selectinload(Book.tags)
    )        
    stmt = filter.filter(query)
    stmt = filter.sort(stmt)
    stmt = stmt.offset(offset).limit(per_page)
    result = await db.execute(stmt)
    return result.unique().scalars().all()


async def count_books(filter: BookFilter, db: AsyncSession) -> int:
    count_query = select(func.count(distinct(Book.id))).select_from(Book).outerjoin(
        Book.publisher).outerjoin(
        Book.categories).outerjoin(
        Book.authors).outerjoin(Book.tags)
    query = filter.filter(count_query)
    return await db.scalar(query)


async def create_book(payload: dict, db: AsyncSession) -> Book:
    _book = await db.scalar(select(Book).where(Book.sku == payload['sku']))
    if _book:
        raise ConflictException(
            'Book with this SKU already exists', str(_book.id))

    payload['slug'] = slugify(payload['slug'])
    payload = await handle_relationship(payload, db)
    if payload.get('images'):
        payload['images'] = (await db.scalars(select(Image).where(Image.id.in_(payload['images'])))).all()

    logger.debug(f'Creating book with payload: {payload}')
    book = Book(**payload)
    db.add(book)
    await db.commit()

    logger.info(f'Book created successfully {book}')
    return book


async def create_book_bulk(payload: list[dict], db: AsyncSession) -> Sequence[Book]:

    try:
        chunk_size = 20000
        main_df = pd.DataFrame(payload)
        main_df = main_df.drop_duplicates(subset=['sku'])
        logger.debug(f'Len after dropping duplicates: {len(main_df)}')

        new_items = []
        for i in range(0, len(main_df), chunk_size):
            df = main_df[i:i+chunk_size]
            _sku = (await db.scalars(select(Book.sku).filter(Book.sku.in_(df['sku'].tolist())))).all()
            df = df[~df['sku'].isin(_sku)]
            logger.debug(f'Len after dropping existing sku: {
                         len(df)}/{chunk_size}')

            if df.empty:
                continue
            data = list(df.T.to_dict().values())
            publishers = {publisher.id: publisher for publisher in await db.scalars(select(Publisher).filter(Publisher.id.in_(df['publisher_id'].unique())))}
            author_ids = {author_id for book in data for author_id in (
                book['authors'] + book['translators'])}
            authors = {author.id: author for author in await db.scalars(select(Author).filter(Author.id.in_(author_ids)))}
            category_ids = {
                category_id for book in data for category_id in book['categories']}
            categories = {category.id: category for category in await db.scalars(select(Category).filter(Category.id.in_(category_ids)))}
            image_ids = {
                image_id for book in data for image_id in book['images']}
            images = {image.id: image for image in await db.scalars(select(Image).filter(Image.id.in_(image_ids)))}
            tag_ids = {tag_id for book in data for tag_id in book['tags']}
            tags = {tag.id: tag for tag in await db.scalars(select(Tag).filter(Tag.id.in_(tag_ids)))}

            items = []
            for book in data:
                book['slug'] = slugify(book['slug'])
                book['publisher'] = publishers.get(book['publisher_id'])
                book['authors'] = [authors[author_id]
                                   for author_id in book['authors']]
                book['translators'] = [authors[translator_id]
                                       for translator_id in book['translators']]
                book['categories'] = [categories[category_id]
                                      for category_id in book['categories']]
                book['images'] = [images[image_id]
                                  for image_id in book['images']]
                book['tags'] = [tags[tag_id] for tag_id in book['tags']]
                item = Book(**book)
                items.append(item)

            logger.debug(f'Adding {len(items)} books')
            db.add_all(items)
            logger.info(f"{len(items)}/{len(payload)
                                        } books created successfully")
            new_items.extend(items)
        await db.commit()
        return new_items
    except Exception:
        logger.error(f"Error creating books: {traceback.format_exc()}")
        raise ServerErrorException('Error creating books. Try again later.')


async def update_book(id: UUID, payload: dict, db: AsyncSession) -> Book:
    book = await db.scalar(query_selectinload.where(Book.id == id))
    if not book:
        raise NotFoundException('Book not found')

    if payload.get('slug'):
        payload['slug'] = slugify(payload['slug'])
    payload = await handle_relationship(payload, db)
    if 'images' in payload:
        previous_ids = [image.id for image in book.images]
        payload['images'] = await handle_multiple_image_attachment(payload['images'], previous_ids, db, book_image_link)

    logger.debug(f'Updating book with payload: {payload}')
    [setattr(book, key, value) for key, value in payload.items()]

    await db.commit()
    logger.info(f'Book updated successfully {book}')
    return book


async def delete_book(id: UUID, db: AsyncSession) -> None:
    book = await db.scalar(select(Book).where(Book.id == id))
    if not book:
        raise NotFoundException('Book not found')

    await handle_multiple_image_attachment([], [image.id for image in await book.awaitable_attrs.images], db, book_image_link)
    await db.delete(book)
    await db.commit()

    logger.info(f'Book deleted successfully {book}')


async def handle_relationship(payload: dict, db: AsyncSession) -> dict:
    if payload.get('publisher_id'):
        payload['publisher'] = await db.get(Publisher, payload['publisher_id'])
    if payload.get('authors'):
        payload['authors'] = (await db.scalars(select(Author).where(Author.id.in_(payload['authors'])))).all()
    if payload.get('translators'):
        payload['translators'] = (await db.scalars(select(Author).where(Author.id.in_(payload['translators'])))).all()
    if payload.get('categories'):
        payload['categories'] = (await db.scalars(select(Category).where(Category.id.in_(payload['categories'])))).all()
    if payload.get('tags'):
        payload['tags'] = (await db.scalars(select(Tag).where(Tag.id.in_(payload['tags'])))).all()

    return payload


async def get_all_books_minimal(filter: BookFilterMinimal, page: int, per_page: int, db: AsyncSession) -> Sequence[Book]:
    offset = (page - 1) * per_page
    query = select(Book).distinct().outerjoin(Book.authors).options(
        selectinload(Book.authors),
        selectinload(Book.images),
    )
    stmt = filter.filter(query)
    stmt = filter.sort(stmt)
    stmt = stmt.offset(offset).limit(per_page)
    result = await db.execute(stmt)
    return result.unique().scalars().all()


async def count_books_minimal(filter: BookFilterMinimal, db: AsyncSession) -> int:
    count_query = select(func.count(distinct(Book.id))).select_from(Book).outerjoin(Book.authors)
    query = filter.filter(count_query)
    return await db.scalar(query)
