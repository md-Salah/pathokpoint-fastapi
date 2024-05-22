import csv
import io
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import UploadFile
import logging

from app.filter_schema.book import BookFilter
from app.models import Publisher
from app.controller.book import get_all_books
from app.controller.exception import NotFoundException


logger = logging.getLogger(__name__)


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
    content = (await file.read()).decode('utf-8').splitlines()
    reader = csv.DictReader(content)

    books = [row for row in reader if any(row.values())]
    logger.info(f'Importing {len(books)} books from CSV file')

    # try:
    #     payload = [CreateBook(**book) for book in books]
    # except ValidationError as err:
    #     logger.error(f'Invalid data in CSV file: {err}')
    #     return str(err)

    return 'ok! But this endpoint is not implemented yet.'
