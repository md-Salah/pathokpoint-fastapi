import csv
import pandas as pd
import io
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from fastapi import UploadFile
import logging

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


async def import_books_from_csv(file: UploadFile, db: AsyncSession):
    if not file.filename:
        raise BadRequestException('Filename not found.')
    elif not file.filename.endswith('.csv'):
        raise BadRequestException(
            'Invalid file format. Only CSV files are allowed.')
    try:
        df = pd.read_csv(file.file, dtype={'edition': str, 'isbn': str})
    except Exception as e:
        raise BadRequestException(f'Error reading CSV file: {str(e)}')

    df.set_index('sku', inplace=True, drop=False)
    err_df = df[['sku']].copy()
    err_df['status'] = ''
    err_df.loc[df.duplicated(subset=['sku']),
               'status'] = 'error: duplicate SKU'
    df = df.drop_duplicates(subset=['sku'])

    chunk_size = 1000
    for i in range(0, len(df), chunk_size):
        chunk_df = df[i:i + chunk_size]
        chunk_df = chunk_df.fillna('')

        try:
            if 'publisher' in chunk_df.columns:
                publisher_names = chunk_df['publisher'].unique()
                existing_publishers = (await db.scalars(select(Publisher).filter(Publisher.name.in_(publisher_names)))).all()
                publishers = {
                    publisher.name: publisher for publisher in existing_publishers}

                if 'publisher_slug' not in chunk_df.columns:
                    chunk_df['publisher_slug'] = ''
                to_create = chunk_df[~chunk_df['publisher'].isin(publishers.keys())][[
                    'publisher', 'publisher_slug']].drop_duplicates().values.tolist()
                new_publishers = {name: Publisher(
                    name=name, slug=(await unique_slug((slug or name), Publisher, db))) for name, slug in to_create}
                publishers.update(new_publishers)

            if 'authors' in chunk_df.columns:
                author_names = set([author.strip() for sublist in chunk_df['authors'].str.split(
                    '|') for author in sublist])
                exitsting_authors = (await db.scalars(select(Author).filter(Author.name.in_(author_names)))).all()
                authors = {author.name: author for author in exitsting_authors}

                if 'authors_slug' not in chunk_df.columns:
                    chunk_df['authors_slug'] = ''
                to_create = chunk_df[['authors',
                                      'authors_slug']].drop_duplicates()
                to_create = to_create[to_create['authors'].str.strip() != '']
                for _, row in to_create.iterrows():
                    for name, slug in zip(row['authors'].split('|'), (row['authors_slug'] or row['authors']).split('|')):
                        name = name.strip()
                        if name and name not in authors:
                            authors[name] = Author(
                                name=name, slug=(await unique_slug(slug, Author, db)))

            if 'translators' in chunk_df.columns:
                translator_names = set([translator.strip(
                ) for sublist in chunk_df['translators'].str.split('|') for translator in sublist])
                existing_translators = (await db.scalars(select(Author).filter(Author.name.in_(translator_names)))).all()
                translators = {
                    translator.name: translator for translator in existing_translators}

                if 'translators_slug' not in chunk_df.columns:
                    chunk_df['translators_slug'] = ''
                to_create = chunk_df[['translators',
                                      'translators_slug']].drop_duplicates()
                to_create = to_create[to_create['translators'].str.strip(
                ) != '']
                for _, row in to_create.iterrows():
                    for name, slug in zip(row['translators'].split('|'), (row['translators_slug'] or row['translators']).split('|')):
                        name = name.strip()
                        if name and name not in translators:
                            translators[name] = Author(
                                name=name, slug=(await unique_slug(slug, Author, db)))

            if 'categories' in chunk_df.columns:
                category_names = set([category.strip(
                ) for sublist in chunk_df['categories'].str.split('|') for category in sublist])
                existing_categories = (await db.scalars(select(Category).filter(Category.name.in_(category_names)))).all()
                categories = {
                    category.name: category for category in existing_categories}

                if 'categories_slug' not in chunk_df.columns:
                    chunk_df['categories_slug'] = ''
                to_create = chunk_df[['categories',
                                      'categories_slug']].drop_duplicates()
                to_create = to_create[to_create['categories'].str.strip(
                ) != '']
                for _, row in to_create.iterrows():
                    for name, slug in zip(row['categories'].split('|'), (row['categories_slug'] or row['categories']).split('|')):
                        name = name.strip()
                        if name and name not in categories:
                            categories[name] = Category(
                                name=name, slug=(await unique_slug(slug, Category, db)))

            if 'tags' in chunk_df.columns:
                tag_names = set(
                    [tag.strip() for sublist in chunk_df['tags'].str.split('|') for tag in sublist])
                existing_tags = (await db.scalars(select(Tag).filter(Tag.name.in_(tag_names)))).all()
                tags = {tag.name: tag for tag in existing_tags}

                if 'tags_slug' not in chunk_df.columns:
                    chunk_df['tags_slug'] = ''
                to_create = chunk_df[['tags', 'tags_slug']].drop_duplicates()
                to_create = to_create[to_create['tags'].str.strip() != '']
                for _, row in to_create.iterrows():
                    for name, slug in zip(row['tags'].split('|'), (row['tags_slug'] or row['tags']).split('|')):
                        name = name.strip()
                        if name and name not in tags:
                            tags[name] = Tag(name=name, slug=(
                                await unique_slug(slug, Tag, db)
                            ))

        except Exception as e:
            logger.error(f'{e.__class__}: {str(e)}')
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
            items = []
            for idx, book in enumerate(books):
                try:
                    book['name'] = book['name'].strip()
                    book['slug'] = book['slug'].strip()
                    assert book['regular_price'] > 0, 'error: regular_price must be greater than 0'
                    assert book['sale_price'] >= 0, 'error: sale_price must be greater than or equal to 0'
                    assert book['regular_price'] >= book['sale_price'], 'error: sale_price must be less than or equal to regular_price'
                    assert book['manage_stock'] in [
                        True, False], 'error: manage_stock must be a boolean'
                    assert book['quantity'] >= 0, 'error: quantity must be greater than or equal to 0'
                    if book['in_stock']:
                        assert book['quantity'] > 0, 'error: quantity must be greater than 0 when in_stock is True'
                    if book['is_used'] is False:
                        assert book['condition'] == Condition.new.value, 'error: condition must be new when is_used is False'
                    book['condition'] = Condition(book['condition'])
                    book['cover'] = Cover(book['cover'])
                    book['language'] = Language(book['language'])
                    book['stock_location'] = StockLocation(
                        book['stock_location']) if 'stock_location' in book else StockLocation.mirpur_11

                    book['publisher'] = publishers.get(book['publisher'])
                    book['authors'] = [authors.get(athr.strip()) for athr in book['authors'].split(
                        '|') if authors.get(athr.strip()) is not None]

                    if 'translators' in book:
                        book['translators'] = [authors.get(athr.strip()) for athr in book['translators'].split(
                            '|') if authors.get(athr.strip()) is not None]
                    if 'categories' in book:
                        book['categories'] = [categories.get(cat.strip()) for cat in book['categories'].split(
                            '|') if categories.get(cat.strip()) is not None]

                    book['tags'] = [tags.get(tag.strip()) for tag in book['tags'].split(
                        '|') if tags.get(tag.strip()) is not None]

                    if 'images' in book:
                        images = []
                        for img in book['images'].split('|'):
                            if img.strip():
                                response = await upload_file_to_cloudinary(img.strip(), None, ImageFolder.book.value)
                                assert response, 'error: image upload failed'
                                image = Image(name=response['filename'],
                                              src=response['secure_url'], alt=book['name'], public_id=response['public_id'], folder=ImageFolder.book)
                                images.append(image)
                        book['images'] = images

                    item = Book(**{k: v for k, v in book.items() if v})
                    if idx == 0:
                        logger.debug(f'Inserting book: {item.__dict__}')
                    items.append(item)
                    err_df.loc[book['sku'], 'status'] = 'successfully inserted'
                except Exception as e:
                    err = f'error: {e.__class__}: {str(e)}'
                    logger.error(err)
                    err_df.loc[book['sku'], 'status'] = err
            db.add_all(items)
        if not updt_df.empty:
            logger.info(f'Updating {len(updt_df)} books')
            updt_df = updt_df[[
                col for col in updt_df.columns if col in db_cols]]
            books = (await db.scalars(query_selectinload.filter(Book.sku.in_(updt_df['sku'])))).all()
            for idx, book in enumerate(books):
                try:
                    values = updt_df.loc[updt_df['sku']
                                         == book.sku].iloc[0].to_dict()
                    for key, value in values.items():
                        if not value:
                            continue
                        if key == 'authors':
                            value = [authors.get(athr.strip()) for athr in value.split(
                                '|') if authors.get(athr.strip()) is not None]
                        elif key == 'translators':
                            value = [authors.get(athr.strip()) for athr in value.split(
                                '|') if authors.get(athr.strip()) is not None]
                        elif key == 'publisher':
                            value = publishers.get(value)
                        elif key == 'categories':
                            value = [categories.get(cat.strip()) for cat in value.split(
                                '|') if categories.get(cat.strip()) is not None]
                        elif key == 'tags':
                            value = [tags.get(tag.strip()) for tag in value.split(
                                '|') if tags.get(tag.strip()) is not None]
                        elif key == 'images':
                            if len(book.images):
                                for img in book.images:
                                    await delete_file_from_cloudinary(img.public_id)
                                await db.execute(book_image_link.delete().where(book_image_link.c.book_id == book.id))
                                await db.execute(delete(Image).where(Image.id.in_([img.id for img in book.images])))
                            images = []
                            for img in value.split('|'):
                                if img.strip():
                                    response = await upload_file_to_cloudinary(img.strip(), None, ImageFolder.book.value)
                                    assert response, 'error: image upload failed'
                                    image = Image(name=response['filename'],
                                                  src=response['secure_url'], alt=book.name, public_id=response['public_id'], folder=ImageFolder.book)
                                    images.append(image)
                            value = images
                        elif key == 'condition':
                            value = Condition(value)
                        elif key == 'cover':
                            value = Cover(value)
                        elif key == 'language':
                            value = Language(value)
                        elif key == 'stock_location':
                            value = StockLocation(value)
                        setattr(book, key, value)
                    if idx == 0:
                        logger.debug(f'Updating book: {book.__dict__}')
                    err_df.loc[book.sku, 'status'] = 'successfully updated'
                except Exception as e:
                    err = f'error: {e.__class__}: {str(e)}'
                    logger.error(err)
                    err_df.loc[book.sku, 'status'] = err
    await db.commit()
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
