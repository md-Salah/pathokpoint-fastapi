import logging
from datetime import datetime

from sqlalchemy import Integer, func, not_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Book, Order, Tag, book_tag_link

logger = logging.getLogger(__name__)


async def order_analysis(from_date: datetime | None, to_date: datetime | None, db: AsyncSession) -> dict:
    query = select(
        func.count(Order.id),
        func.sum(Order.total),
        func.sum(Order.new_book_total),
        func.sum(Order.old_book_total),
        func.sum(Order.cost_of_good_new),
        func.sum(Order.cost_of_good_old),
        func.sum(Order.shipping_charge),
        func.sum(Order.weight_charge)
    )

    if from_date and to_date:
        query = query.filter(Order.created_at.between(from_date, to_date))
    elif from_date:
        query = query.filter(Order.created_at >= from_date)
    elif to_date:
        query = query.filter(Order.created_at <= to_date)

    logger.debug(f'Query: {query}')

    result = (await db.execute(query))
    (
        total_order,
        order_value,
        order_value_new_book,
        order_value_old_book,
        cog_new_book,
        cog_old_book,
        shipping_charge,
        weight_charge
    ) = result.all()[0]

    return {
        'total_order': total_order,
        'order_value': order_value or 0,
        'order_value_new_book': order_value_new_book or 0,
        'order_value_old_book': order_value_old_book or 0,
        'cog_new_book': cog_new_book or 0,
        'cog_old_book': cog_old_book or 0,
        'profit': (order_value - shipping_charge - weight_charge - cog_new_book - cog_old_book) if total_order else 0,
        'shipping_charge': shipping_charge or 0,
        'weight_charge': weight_charge or 0
    }


async def inventory_analysis(db: AsyncSession) -> list[dict]:
    query = select(
        Tag.name,
        func.sum(Book.quantity),
        func.count(Book.id),
        func.sum(func.cast(Book.in_stock, Integer)),
        func.sum(func.cast(not_(Book.in_stock), Integer)),
        func.sum(Book.cost * Book.quantity),
        func.sum(Book.regular_price * Book.quantity),
        func.sum(Book.sale_price * Book.quantity)
    ).select_from(Tag).join(book_tag_link, Tag.id == book_tag_link.c.tag_id).join(Book, book_tag_link.c.book_id == Book.id).group_by(Tag.name)

    result = (await db.execute(query))
    group = []
    for row in result.all():
        tag, quantity, unique_product, in_stock, out_of_stock, cost, regular_price, sale_price = row
        group.append({
            'tag': tag,
            'quantity': quantity,
            'unique_product': unique_product,
            'in_stock': in_stock,
            'out_of_stock': out_of_stock,
            'cost': cost,
            'regular_price': regular_price,
            'sale_price': sale_price
        })
    # logger.debug(f'Group: {group}')
    return group
