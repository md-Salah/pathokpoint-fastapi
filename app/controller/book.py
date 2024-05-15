from fastapi import HTTPException, status
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete, update
from uuid import UUID
from typing import Sequence
from sqlalchemy.orm import joinedload
import logging

from slugify import slugify

from app.filter_schema.book import BookFilter
from app.models import Book, Author, Category, Image, Publisher, Tag


logger = logging.getLogger(__name__)

book_query = select(Book).options(
    joinedload(Book.publisher),
    joinedload(Book.authors),
    joinedload(Book.translators),
    joinedload(Book.categories),
    joinedload(Book.images),
    joinedload(Book.tags)
)


async def get_book_by_id(id: UUID, db: AsyncSession) -> Book:
    book = await db.scalar(book_query.where(Book.id == id))
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Book with id {id} not found')
    return book


async def get_all_books(page: int, per_page: int, db: AsyncSession,
                        book_filter: BookFilter,
                        authors: str | None,
                        categories: str | None,
                        publishers: str | None,
                        translators: str | None,
                        tags: str | None) -> Sequence[Book]:
    offset = (page - 1) * per_page

    query = book_filter.filter(book_query)
    query = query.offset(offset).limit(per_page)

    if authors:
        query = query.filter(Book.authors.any(
            Author.slug.in_(authors.split(','))))
    if categories:
        query = query.filter(Book.categories.any(
            Category.slug.in_(categories.split(','))))
    if publishers:
        query = query.filter(Book.publisher.slug.in_(
            publishers.split(',')))
    if translators:
        query = query.filter(Book.translators.any(
            Author.slug.in_(translators.split(','))))
    if tags:
        query = query.filter(Book.tags.any(
            Tag.slug.in_(tags.split(','))))

    result = await db.execute(query)
    books = result.unique().scalars().all()
    return books


async def count_books(db: AsyncSession, book_filter: BookFilter,
                      authors: str | None,
                      categories: str | None,
                      publishers: str | None,
                      translators: str | None,
                      tags: str | None) -> int:
    query = select(func.count(Book.id))
    query = book_filter.filter(query)

    if authors:
        query = query.join(Book.authors).filter(
            Author.slug.in_(authors.split(',')))
    if categories:
        query = query.join(Book.categories).filter(
            Category.slug.in_(categories.split(',')))
    if publishers:
        query = query.join(Book.publisher).filter(
            Publisher.slug.in_(publishers.split(',')))
    if translators:
        query = query.join(Book.translators).filter(
            Author.slug.in_(translators.split(',')))
    if tags:
        query = query.join(Book.tags).filter(
            Tag.slug.in_(tags.split(',')))

    return await db.scalar(query)


async def create_book(payload: dict, db: AsyncSession) -> Book:
    _book = await db.scalar(select(Book).where(Book.sku == payload['sku']))
    if _book:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail={
                                'msg': 'Book with sku ({}) already exists'.format(payload['sku']),
                                'resource_id': str(_book.id),
                            })

    payload['slug'] = slugify(payload['slug'])
    payload = await build_relationships(payload, db)

    book = Book(**payload)
    db.add(book)
    await db.commit()

    return book


async def create_book_bulk(payload: list[dict], db: AsyncSession) -> Sequence[Book]:

    _sku = [book.sku for book in await db.scalars(select(Book).filter(Book.sku.in_([book['sku'] for book in payload])))]
    books = [book for book in payload if book['sku'] not in _sku]

    publisher_ids = {book['publisher'] for book in books}
    publishers = {publisher.id: publisher for publisher in await db.scalars(select(Publisher).filter(Publisher.id.in_(publisher_ids)))}

    author_ids = {author_id for book in books for author_id in (book['authors'] + book['translators'])}
    authors = {author.id: author for author in await db.scalars(select(Author).filter(Author.id.in_(author_ids)))}
    
    category_ids = {category_id for book in books for category_id in book['categories']}
    categories = {category.id: category for category in await db.scalars(select(Category).filter(Category.id.in_(category_ids)))}

    image_ids = {image_id for book in books for image_id in book['images']}
    images = {image.id: image for image in await db.scalars(select(Image).filter(Image.id.in_(image_ids)))}

    tag_ids = {tag_id for book in books for tag_id in book['tags']}
    tags = {tag.id: tag for tag in await db.scalars(select(Tag).filter(Tag.id.in_(tag_ids)))}

    logger.debug(f'Creating {len(books)} books with payload: {books[0]}')
    new_items = []
    for book in books:
        book['slug'] = slugify(book['slug'])
        
        book['publisher'] = publishers[book['publisher']]
        book['authors'] = [authors[author_id] for author_id in book['authors']]
        book['translators'] = [authors[translator_id] for translator_id in book['translators']]
        book['categories'] = [categories[category_id] for category_id in book['categories']]
        book['images'] = [images[image_id] for image_id in book['images']]
        book['tags'] = [tags[tag_id] for tag_id in book['tags']]
        
        new_item = Book(**book)
        new_items.append(new_item)

    db.add_all(new_items)
    await db.commit()
    logger.info(f"{len(new_items)}/{len(payload)} books created successfully")
    return new_items


async def update_book(id: UUID, payload: dict, db: AsyncSession) -> Book:
    book = await db.scalar(book_query.where(Book.id == id))
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Book with id ({id}) not found')

    if payload.get('slug'):
        payload['slug'] = slugify(payload['slug'])
    payload = await build_relationships(payload, db)

    [setattr(book, key, value) for key, value in payload.items()]

    await db.commit()
    return book


async def delete_book(id: UUID, db: AsyncSession) -> None:
    await db.execute(delete(Book).where(Book.id == id))
    await db.commit()


# async def build_relationships(payload: dict, db: AsyncSession) -> dict:
#     if payload.get('publisher'):
#         payload['publisher'] = await db.get(Publisher, payload['publisher'])
#     if payload.get('authors'):
#         payload['authors'] = [await db.get(Author, author_id) for author_id in payload['authors']]
#     if payload.get('translators'):
#         payload['translators'] = [await db.get(Author, translator_id) for translator_id in payload['translators']]
#     if payload.get('categories'):
#         payload['categories'] = [await db.get(Category, category_id) for category_id in payload['categories']]
#     if payload.get('images'):
#         payload['images'] = [await db.get(Image, image_id) for image_id in payload['images']]
#     if payload.get('tags'):
#         payload['tags'] = [await db.get(Tag, tag_id) for tag_id in payload['tags']]

#     return payload

async def build_relationships(payload: dict, db: AsyncSession) -> dict:
    tasks = []

    if payload.get('publisher'):
        tasks.append(db.get(Publisher, payload['publisher']))

    if payload.get('authors'):
        tasks += [db.get(Author, author_id)
                  for author_id in payload['authors']]

    if payload.get('translators'):
        tasks += [db.get(Author, translator_id)
                  for translator_id in payload['translators']]

    if payload.get('categories'):
        tasks += [db.get(Category, category_id)
                  for category_id in payload['categories']]

    if payload.get('images'):
        tasks += [db.get(Image, image_id) for image_id in payload['images']]

    if payload.get('tags'):
        tasks += [db.get(Tag, tag_id) for tag_id in payload['tags']]

    results = await asyncio.gather(*tasks)

    # Now, map the results back to the payload, noting that the results order matches the tasks order
    iterator = iter(results)
    if payload.get('publisher'):
        payload['publisher'] = next(iterator)

    if payload.get('authors'):
        payload['authors'] = [next(iterator) for _ in payload['authors']]

    if payload.get('translators'):
        payload['translators'] = [next(iterator)
                                  for _ in payload['translators']]

    if payload.get('categories'):
        payload['categories'] = [next(iterator) for _ in payload['categories']]

    if payload.get('images'):
        payload['images'] = [next(iterator) for _ in payload['images']]

    if payload.get('tags'):
        payload['tags'] = [next(iterator) for _ in payload['tags']]

    return payload
