import io
import csv
import pandas as pd
import numpy as np
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from fastapi import UploadFile
import logging
from typing import Any
import traceback

from app.constant import Condition, Cover, Language, StockLocation, ImageFolder
from app.filter_schema.book import BookFilter
from app.models import Book, Author, Publisher, Category, Tag, Image
from app.models.book import book_image_link
from app.controller.book import get_all_books
from app.library.cloudinary import upload_file_to_cloudinary, delete_file_from_cloudinary
from app.controller.exception import NotFoundException, BadRequestException
from app.controller.utility import unique_slug

logger = logging.getLogger(__name__)

query_selectinload = select(Book).options(
    selectinload(Book.publisher),
    selectinload(Book.authors),
    selectinload(Book.translators),
    selectinload(Book.categories),
    selectinload(Book.images),
    selectinload(Book.tags)
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


def int_cast(num: str | int | float) -> int | None:
    try:
        return int(num)
    except Exception:
        return None


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


async def find_or_create(name_str: str | None, slug_str: str | None, hash: dict, cls: Any, db: AsyncSession):
    if not name_str:
        return []
    slug = {name.strip(): slug.strip() for name, slug in zip(
        name_str.split('|'), slug_str.split('|'))} if slug_str else {}
    items = []
    for name in name_str.split('|'):
        name = name.strip()
        if name:
            if name in hash:
                items.append(hash[name])
            else:
                new_item = cls(
                    name=name, slug=(
                        await unique_slug(slug.get(name) or name, cls, db)
                    ))
                hash[name] = new_item
                items.append(new_item)
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
    err_df = df[['sku']].copy()
    err_df['status'] = ''

    chunk_size = 1000
    for i in range(0, len(df), chunk_size):
        chunk_df = df[i:i + chunk_size]
        chunk_df = chunk_df.fillna(np.nan).replace([np.nan], [None])

        try:
            if 'publisher' in chunk_df.columns:
                publisher_names = chunk_df['publisher'].unique()
                existing_publishers = (await db.scalars(select(Publisher).filter(Publisher.name.in_(publisher_names)))).all()
                publishers = {
                    publisher.name: publisher for publisher in existing_publishers}

            if 'authors' in chunk_df.columns:
                author_names = df['authors'].str.split('|').explode().unique()
                author_names = [
                    author.strip() for author in author_names if author and not pd.isna(author)]
                exitsting_authors = (await db.scalars(select(Author).filter(Author.name.in_(author_names)))).all()
                authors = {author.name: author for author in exitsting_authors}

            if 'translators' in chunk_df.columns:
                translator_names = df['translators'].str.split(
                    '|').explode().unique()
                translator_names = [translator.strip(
                ) for translator in translator_names if translator and not pd.isna(translator)]
                existing_translators = (await db.scalars(select(Author).filter(Author.name.in_(translator_names)))).all()
                translators = {
                    translator.name: translator for translator in existing_translators}

            if 'categories' in chunk_df.columns:
                category_names = df['categories'].str.split(
                    '|').explode().unique()
                category_names = [category.strip(
                ) for category in category_names if category and not pd.isna(category)]
                existing_categories = (await db.scalars(select(Category).filter(Category.name.in_(category_names)))).all()
                categories = {
                    category.name: category for category in existing_categories}

            if 'tags' in chunk_df.columns:
                tag_names = df['tags'].str.split('|').explode().unique()
                tag_names = [tag.strip()
                             for tag in tag_names if tag and not pd.isna(tag)]
                existing_tags = (await db.scalars(select(Tag).filter(Tag.name.in_(tag_names)))).all()
                tags = {tag.name: tag for tag in existing_tags}

            for col in ['short_description', 'edition', 'notes', 'description', 'isbn', 'country', 'shelf', 'row_col', 'bar_code']:
                if col in chunk_df.columns:
                    chunk_df[col] = chunk_df[col].apply(
                        lambda x: x.strip() if x else None)

        except Exception as e:
            logger.error(f'{traceback.format_exc()}')
            raise BadRequestException(f'Error processing data: {str(e)}')

        existing_skus = (await db.scalars(select(Book.sku).filter(Book.sku.in_(chunk_df['sku'].tolist())))).all()
        updt_df = chunk_df[chunk_df['sku'].isin(existing_skus)]
        chunk_df = chunk_df[~chunk_df['sku'].isin(existing_skus)]

        if not chunk_df.empty:
            missing_cols = list(reqd_cols - set(chunk_df.columns))
            if missing_cols:
                raise BadRequestException(
                    f'Columns are required: {", ".join(missing_cols)}')

            logger.info(f'Inserting {len(chunk_df)} books')
            chunk_df = chunk_df[[
                col for col in chunk_df.columns if col in db_cols]]
            books = list(chunk_df.T.to_dict().values())

            for idx, book in enumerate(books):
                try:
                    book['name'] = book['name'].strip()
                    book['slug'] = book['slug'].strip()
                    assert book['regular_price'] > 0, 'error: regular_price must be greater than to 0'
                    assert book['sale_price'] > 0, 'error: sale_price must be greater than to 0'
                    assert book['regular_price'] >= book['sale_price'], 'error: sale_price must be less than or equal to regular_price'
                    assert book['manage_stock'] in [
                        True, False], 'error: manage_stock must be a boolean'
                    assert book['quantity'] >= 0, 'error: quantity must be greater than or equal to 0'
                    if book['in_stock']:
                        assert book['quantity'] > 0, 'error: quantity must be greater than 0 when in_stock is True'
                    if book['is_used'] is False:
                        assert book['condition'] == Condition.new.value, 'error: condition must be new when is_used is False'
                    book['condition'] = Condition(book['condition'])
                    book['cover'] = Cover(
                        book['cover']) if book['cover'] else None
                    book['language'] = Language(
                        book['language']) if book['language'] else None
                    book['stock_location'] = StockLocation(
                        book['stock_location']) if 'stock_location' in book else StockLocation.mirpur_11

                    if book['publisher']:
                        book['publisher'] = book['publisher'].strip()
                        if book['publisher'] in publishers:
                            book['publisher'] = publishers[book['publisher']]
                        else:
                            book['publisher'] = Publisher(name=book['publisher'].strip(),
                                                          slug=(await unique_slug(book.get('publisher_slug') or book['publisher'], Publisher, db)))
                            publishers[book['publisher'].name] = book['publisher']

                    book['authors'] = await find_or_create(book['authors'], book.get('authors_slug'), authors, Author, db)
                    book['translators'] = await find_or_create(book['translators'], book.get('translators_slug'), translators, Author, db)
                    book['categories'] = await find_or_create(book['categories'], book.get('categories_slug'), categories, Category, db)
                    book['tags'] = await find_or_create(book['tags'], book.get('tags_slug'), tags, Tag, db)

                    if book.get('images'):
                        images = []
                        for img in book['images'].split('|'):
                            if img.strip():
                                response = await upload_file_to_cloudinary(img.strip(), None, ImageFolder.book.value)
                                assert response, 'error: image upload failed'
                                image = Image(name=response['filename'],
                                              src=response['secure_url'], alt=book['name'], public_id=response['public_id'], folder=ImageFolder.book)
                                images.append(image)
                        book['images'] = images
                    else:
                        book['images'] = []

                    if book.get('no_of_pages'):
                        book['no_of_pages'] = int_cast(book['no_of_pages'])

                    item = Book(**{k: v for k, v in book.items() if v})
                    db.add(item)
                    await db.commit()
                    err_df.loc[book['sku'], 'status'] = 'successfully inserted'

                    if idx == 0:
                        logger.debug(f'Inserting book: {item.__dict__}')
                except Exception as e:
                    if book.get('images') and isinstance(book['images'][0], Image):
                        for img in book['images']:
                            await delete_file_from_cloudinary(img.public_id)
                        await db.rollback()

                    logger.error(f'{traceback.format_exc()}')
                    err_df.loc[book['sku'], 'status'] = 'error: {}: {}'.format(
                        e.__class__, str(e))

        if not updt_df.empty:
            logger.info(f'Updating {len(updt_df)} books')
            updt_df = updt_df[[
                col for col in updt_df.columns if col in db_cols]]
            books = (await db.scalars(query_selectinload.filter(Book.sku.in_(updt_df['sku'])))).all()
            for idx, book in enumerate(books):
                try:
                    _book = updt_df.loc[updt_df['sku']
                                        == book.sku].iloc[0].to_dict()
                    for key, val in _book.items():
                        if isinstance(val, str):
                            val = val.strip()
                        if not val:
                            continue
                        if key == 'authors':
                            val = await find_or_create(val, _book.get('authors_slug'), authors, Author, db)
                        elif key == 'translators':
                            val = await find_or_create(val, _book.get('translators_slug'), translators, Author, db)
                        elif key == 'publisher':
                            if val in publishers:
                                val = publishers[val]
                            else:
                                new_publisher = Publisher(
                                    name=val, slug=(await unique_slug(_book.get('publisher_slug') or val, Publisher, db)))
                                publishers[val] = new_publisher
                                val = new_publisher
                        elif key == 'categories':
                            val = await find_or_create(val, _book.get('categories_slug'), categories, Category, db)
                        elif key == 'tags':
                            val = await find_or_create(val, _book.get('tags_slug'), tags, Tag, db)
                        elif key == 'images':
                            if len(book.images):
                                for img in book.images:
                                    await delete_file_from_cloudinary(img.public_id)
                                await db.execute(book_image_link.delete().where(book_image_link.c.book_id == book.id))
                                await db.execute(delete(Image).where(Image.id.in_([img.id for img in book.images])))
                            images = []
                            for img in val.split('|'):
                                if img.strip():
                                    response = await upload_file_to_cloudinary(img.strip(), None, ImageFolder.book.value)
                                    assert response, 'error: image upload failed'
                                    image = Image(name=response['filename'],
                                                  src=response['secure_url'], alt=book.name, public_id=response['public_id'], folder=ImageFolder.book)
                                    images.append(image)
                            val = images
                        elif key == 'condition':
                            val = Condition(val)
                        elif key == 'cover':
                            val = Cover(val)
                        elif key == 'language':
                            val = Language(val)
                        elif key == 'stock_location':
                            val = StockLocation(val)
                        elif key == 'no_of_pages':
                            val = int_cast(val)
                        setattr(book, key, val)

                    await db.commit()
                    err_df.loc[book.sku, 'status'] = 'successfully updated'

                    if idx == 0:
                        logger.debug(f'Updated: {book.__dict__}')
                except Exception as e:
                    logger.error(f'{traceback.format_exc()}')
                    err_df.loc[book.sku, 'status'] = f'error: {
                        e.__class__}: {str(e)}'

    df['status'] = err_df['status']
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
