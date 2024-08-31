import io
import csv
import pandas as pd
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload, joinedload
from fastapi import UploadFile
import logging
from typing import Any
import traceback

from app.constant import ImageFolder
from app.filter_schema.book import BookFilter
from app.models import Book, Author, Publisher, Category, Tag, Image
from app.controller.book import get_all_books
from app.library.cloudinary import upload_file_to_cloudinary, delete_file_from_cloudinary
from app.controller.exception import NotFoundException, BadRequestException
from app.controller.utility import unique_slug

from app.pydantic_schema.book import CreateBook, UpdateBook
from app.pydantic_schema.author import CreateAuthor
from app.pydantic_schema.publisher import CreatePublisher
from app.pydantic_schema.category import CreateCategory
from app.pydantic_schema.tag import CreateTag


logger = logging.getLogger(__name__)

query_selectinload = select(Book).options(
    selectinload(Book.publisher),
    selectinload(Book.authors),
    selectinload(Book.translators),
    selectinload(Book.categories),
    selectinload(Book.images),
    selectinload(Book.tags)
)

query_joinedload = select(Book).options(
    joinedload(Book.publisher),
    joinedload(Book.authors),
    joinedload(Book.translators),
    joinedload(Book.categories),
    joinedload(Book.images),
    joinedload(Book.tags)
)

db_cols = Book.__table__.columns.keys(
) + ['authors', 'translators', 'publisher', 'categories', 'tags', 'images']
reqd_cols = {'sku', 'name', 'slug', 'authors', 'publisher', 'regular_price', 'sale_price', 'quantity', 'manage_stock', 'in_stock', 'is_used',
             'condition', 'cover', 'language', 'tags', 'stock_location'}


def flatten(value):
    if isinstance(value, list):
        value = '| '.join([item.name for item in value])
    elif isinstance(value, Publisher):
        value = value.name
    return value


async def export_books_to_csv(filter: BookFilter, page: int, per_page: int, db: AsyncSession, columns: str | None = None):
    books, count = await get_all_books(filter, page, per_page, db)
    if not books:
        raise NotFoundException('No books found')

    headers = list(books[0].__dict__.keys())
    headers.remove('_sa_instance_state')
    if columns:
        columns_list = [col.strip()
                        for col in columns.split(',') if col.strip() in headers]
        headers = sorted(columns_list, key=lambda x: columns_list.index(x))
    else:
        desired_order = [
            'id', 'sku', 'name', 'regular_price', 'sale_price', 'quantity', 'manage_stock',
            'authors', 'publisher', 'categories', 'images', 'tags'
        ]
        headers = sorted(headers, key=lambda x: (x not in desired_order, x.startswith(
            "is_"), desired_order.index(x) if x in desired_order else x))

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(headers)
    for book in books:
        writer.writerow([flatten(getattr(book, header)) for header in headers])
    buffer.seek(0)

    response = StreamingResponse(
        iter([buffer.getvalue()]), media_type='text/csv')
    response.headers['Content-Disposition'] = 'attachment; filename="books.csv"'

    logger.info(f'Exported {len(books)} books to CSV')
    return response, count


async def find_or_create_relation(name_str: str | None, slug_str: str | None,
                                  schema: Any,
                                  cls: Any, db: AsyncSession):
    if not name_str:
        return []
    
    if isinstance(slug_str, float):
        print("slug str debug:", name_str, slug_str)
    slug = {name.strip(): slug.strip() for name, slug in zip(
        name_str.split('|'), slug_str.split('|'))} if slug_str else {}
    items = []
    for name in name_str.split('|'):
        name = name.strip()
        if name:
            entity = await db.scalar(select(cls).filter(cls.name == name))
            if entity:
                items.append(entity)
            else:

                pydantic_item = schema(name=name, slug=(await unique_slug(slug.get(name) or name, cls, db)))
                new_item = cls(**pydantic_item.model_dump())
                items.append(new_item)
    return items


async def upload_images(images: str | None) -> list[Image]:
    if not images:
        return []
    items = []
    for img in images.split('|'):
        if img.strip():
            response = await upload_file_to_cloudinary(img.strip(), None, ImageFolder.book.value)
            assert response, 'error: image upload failed'
            image = Image(name=response['filename'],
                          src=response['secure_url'], public_id=response['public_id'], folder=ImageFolder.book)
            items.append(image)
    return items


async def import_books_from_csv(file: UploadFile, db: AsyncSession):
    if not file.filename:
        raise BadRequestException('Filename not found.')
    elif not file.filename.endswith('.csv'):
        raise BadRequestException(
            'Invalid file format. Only CSV files are allowed.')
    try:
        df = pd.read_csv(file.file, dtype={
                         'edition': str, 'isbn': str, 'translators': str, 'categories': str, 'tags': str, 'authors': str})
    except Exception as e:
        raise BadRequestException(f'Error reading CSV file: {str(e)}')

    df = df.drop_duplicates(subset=['sku'])
    df.set_index('sku', inplace=True, drop=False)
    df['status'] = ''

    for idx, row in df.iterrows():
        try:
            payload = row.dropna().to_dict()
            authors = await find_or_create_relation(payload.pop('authors', None),
                                                    payload.get('authors_slug'), CreateAuthor, Author, db)
            categories = await find_or_create_relation(payload.pop('categories', None),
                                                       payload.get('categories_slug'), CreateCategory, Category, db)
            tags = await find_or_create_relation(payload.pop('tags', None),
                                                 payload.get('tags_slug'), CreateTag, Tag, db)
            publisher = await find_or_create_relation(payload.pop('publisher', None),
                                                      payload.get('publisher_slug'), CreatePublisher, Publisher, db)
            images = await upload_images(payload.pop('images', None))

            _book = await db.scalar(query_joinedload.filter(Book.sku == idx))
            if _book:
                # Update
                pydantic_book = UpdateBook(**payload)
                for key, val in pydantic_book.model_dump(exclude_unset=True).items():
                    setattr(_book, key, val)
                if authors:
                    _book.authors = authors
                if categories:
                    _book.categories = categories
                if tags:
                    _book.tags = tags
                if publisher:
                    _book.publisher = publisher[0]
                if images:
                    _book.images = images

                await db.commit()
                df.at[idx, 'status'] = 'successfully updated'
            else:
                # Insert
                pydantic_book = CreateBook(**payload)
                book = Book(**pydantic_book.model_dump())
                book.authors = authors
                book.categories = categories
                book.tags = tags
                book.publisher = publisher[0]
                book.images = images

                db.add(book)
                await db.commit()
                df.at[idx, 'status'] = 'successfully inserted'
        except Exception as e:
            logger.error(f'{traceback.format_exc()}')
            df.at[idx, 'status'] = 'error: {}: {}'.format(
                e.__class__, str(e))

            try:
                # Remove images from cloudinary
                if isinstance(images[0], Image):
                    for image in images:
                        await delete_file_from_cloudinary(image.public_id)
            except Exception:
                pass

    buffer = io.StringIO()
    df.to_csv(buffer, index=False, encoding='utf-8-sig')
    buffer.seek(0)
    response = StreamingResponse(
        iter([buffer.getvalue()]), media_type='text/csv')
    response.headers['Content-Disposition'] = (
        f'attachment; filename="{file.filename}"'
    )
    return response


async def template_for_import_csv(reqd_cols_only: bool = False):
    attrs = list(reqd_cols) if reqd_cols_only else (db_cols + ['authors_slug',
                                                               'translators_slug', 'categories_slug', 'tags_slug'])
    attrs.sort()
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(attrs)
    buffer.seek(0)

    response = StreamingResponse(
        iter([buffer.getvalue()]), media_type='text/csv')
    response.headers['Content-Disposition'] = 'attachment; filename="template.csv"'
    return response
