from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from uuid import UUID
from typing import Sequence
from sqlalchemy.orm import joinedload, selectinload
import logging
from slugify import slugify


from app.filter_schema.book import BookFilter, BookFilterMinimal
from app.models import Book, Author, Category, Image, Publisher, Tag
from app.controller.exception import NotFoundException, ConflictException


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
    query = select(Book).outerjoin(Book.publisher).outerjoin(Book.categories).outerjoin(Book.authors).outerjoin(Book.images).outerjoin(Book.tags).options(
        joinedload(Book.publisher),
        joinedload(Book.categories),
        joinedload(Book.authors),
        joinedload(Book.translators),
        joinedload(Book.images),
        joinedload(Book.tags)
    )

    stmt = filter.filter(query)
    stmt = filter.sort(stmt)
    stmt = stmt.offset(offset).limit(per_page)
    result = await db.execute(stmt)
    return result.unique().scalars().all()


async def count_books(filter: BookFilter, db: AsyncSession) -> int:
    count_query = select(func.count()).select_from(
        Book).outerjoin(Book.publisher).outerjoin(Book.categories).outerjoin(Book.authors).outerjoin(Book.images).outerjoin(Book.tags)
    query = filter.filter(count_query)
    return await db.scalar(query)


async def create_book(payload: dict, db: AsyncSession) -> Book:
    _book = await db.scalar(select(Book).where(Book.sku == payload['sku']))
    if _book:
        raise ConflictException(
            'Book with this SKU already exists', str(_book.id))

    payload['slug'] = slugify(payload['slug'])
    payload = await handle_relationship(payload, db)

    logger.debug(f'Creating book with payload: {payload}')
    book = Book(**payload)
    db.add(book)
    await db.commit()

    logger.info(f'Book created successfully {book}')
    return book


async def create_book_bulk(payload: list[dict], db: AsyncSession) -> Sequence[Book]:

    _sku = [book.sku for book in await db.scalars(select(Book).filter(Book.sku.in_([book['sku'] for book in payload])))]
    payload = [book for book in payload if book['sku'] not in _sku]

    publisher_ids = {book['publisher_id'] for book in payload}
    publishers = {publisher.id: publisher for publisher in await db.scalars(select(Publisher).filter(Publisher.id.in_(publisher_ids)))}

    author_ids = {author_id for book in payload for author_id in (
        book['authors'] + book['translators'])}
    authors = {author.id: author for author in await db.scalars(select(Author).filter(Author.id.in_(author_ids)))}

    category_ids = {
        category_id for book in payload for category_id in book['categories']}
    categories = {category.id: category for category in await db.scalars(select(Category).filter(Category.id.in_(category_ids)))}

    image_ids = {image_id for book in payload for image_id in book['images']}
    images = {image.id: image for image in await db.scalars(select(Image).filter(Image.id.in_(image_ids)))}

    tag_ids = {tag_id for book in payload for tag_id in book['tags']}
    tags = {tag.id: tag for tag in await db.scalars(select(Tag).filter(Tag.id.in_(tag_ids)))}

    logger.debug(f'Creating {len(payload)} books with payload: {payload[0]}')
    new_items = []
    for book in payload:
        book['slug'] = slugify(book['slug'])

        book['publisher'] = publishers[book['publisher_id']]
        book['authors'] = [authors[author_id] for author_id in book['authors']]
        book['translators'] = [authors[translator_id]
                               for translator_id in book['translators']]
        book['categories'] = [categories[category_id]
                              for category_id in book['categories']]
        book['images'] = [images[image_id] for image_id in book['images']]
        book['tags'] = [tags[tag_id] for tag_id in book['tags']]

        new_item = Book(**book)
        new_items.append(new_item)

    db.add_all(new_items)
    await db.commit()
    logger.info(f"{len(new_items)}/{len(payload)} books created successfully")
    return new_items


async def update_book(id: UUID, payload: dict, db: AsyncSession) -> Book:
    book = await db.scalar(query_selectinload.where(Book.id == id))
    if not book:
        raise NotFoundException('Book not found')

    if payload.get('slug'):
        payload['slug'] = slugify(payload['slug'])
    payload = await handle_relationship(payload, db)

    logger.debug(f'Updating book with payload: {payload}')
    [setattr(book, key, value) for key, value in payload.items()]

    await db.commit()
    logger.info(f'Book updated successfully {book}')
    return book


async def delete_book(id: UUID, db: AsyncSession) -> None:
    book = await db.scalar(select(Book).where(Book.id == id))
    if not book:
        raise NotFoundException('Book not found')
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
    if payload.get('images'):
        payload['images'] = (await db.scalars(select(Image).where(Image.id.in_(payload['images'])))).all()
    if payload.get('tags'):
        payload['tags'] = (await db.scalars(select(Tag).where(Tag.id.in_(payload['tags'])))).all()

    return payload


async def get_all_books_minimal(filter: BookFilterMinimal, page: int, per_page: int, db: AsyncSession) -> Sequence[Book]:
    offset = (page - 1) * per_page
    query = select(Book).outerjoin(Book.authors).outerjoin(Book.images).options(
        joinedload(Book.authors),
        joinedload(Book.images),
    )

    stmt = filter.filter(query)
    stmt = filter.sort(stmt)
    stmt = stmt.offset(offset).limit(per_page)
    result = await db.execute(stmt)
    return result.unique().scalars().all()


async def count_books_minimal(filter: BookFilterMinimal, db: AsyncSession) -> int:
    count_query = select(func.count()).select_from(
        Book).outerjoin(Book.authors).outerjoin(Book.images)
    query = filter.filter(count_query)
    return await db.scalar(query)
