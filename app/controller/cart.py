from sqlalchemy.ext.asyncio import AsyncSession
import logging
from sqlalchemy import select

from app.controller.coupon import get_coupon_by_code
import app.controller.order as order_service
from app.models import OrderItem, Book

logger = logging.getLogger(__name__)


async def apply_coupon(payload: dict, db: AsyncSession):
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
            is_removed=False
        ))
    _, discount, shipping_charge = await order_service.apply_coupon(
        coupon_id=coupon,
        items=items,
        shipping_charge=float('inf'),
        db=db)
    return {
        "discount": discount,
        "shipping_charge": -1 if shipping_charge == float('inf') else shipping_charge
    }
