from sqlalchemy.ext.asyncio import AsyncSession
import logging
from sqlalchemy import select
from typing import Any

from app.controller.coupon import get_coupon_by_code
import app.controller.order as order_service
from app.models import OrderItem, Book
from app.controller.exception import NotFoundException, BadRequestException

logger = logging.getLogger(__name__)


async def apply_coupon(payload: dict[str, Any], db: AsyncSession):
    coupon = await get_coupon_by_code(payload['coupon_code'], db)

    books = await db.scalars(select(Book).where(Book.id.in_([item['book_id'] for item in payload['order_items']])))
    books = {book.id: book for book in books}
    items = []
    for item in payload['order_items']:
        book = books[item['book_id']]
        items.append(OrderItem(
            book=book,
            regular_price=book.regular_price,
            sold_price=book.sale_price,
            quantity=item['quantity'],
        ))
    _, discount, shipping_charge = await order_service.apply_coupon(
        coupon_id=coupon,
        items=items,
        shipping_charge=float('inf'),
        db=db
    )
    return {
        "discount": discount,
        "shipping_charge": -1 if shipping_charge == float('inf') else shipping_charge
    }


async def verify_stock(payload: dict[str, Any], db: AsyncSession):
    ids = [item['book_id'] for item in payload['order_items']]
    books = await db.scalars(select(Book).where(Book.id.in_(ids)))
    books = {book.id: book for book in books}

    for item in payload['order_items']:
        book_id = item['book_id']
        book = books.get(book_id)
        if not book:
            raise NotFoundException('Book not found', str(book_id))

        if not book.in_stock:
            raise BadRequestException(
                "Book '{}' is out of stock".format(book.name), str(book.id))

        if book.manage_stock and book.quantity < item['quantity']:
            raise BadRequestException(
                "Book '{}' has insufficient stock".format(book.name), str(book.id))

    return {"status": "ok"}
