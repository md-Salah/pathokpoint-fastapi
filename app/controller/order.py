from fastapi import HTTPException
from datetime import datetime
import app.pydantic_schema.order as schema
from typing import List


orders = []


async def create_order(order:schema.CreateOrder) -> schema.ReadOrder:
    new_book_total = 500
    old_book_total = 400
    shipping_charge = 100
    weight_charge = 0
    total = new_book_total + old_book_total + shipping_charge + weight_charge
    discount = 20

    new_order = {
        'id': len(orders) + 1,
        'books': order.books,
        'shipping_method': order.shipping_method,
        'coupon_code': order.coupon_code,
        'transaction_ids': [order.transaction_ids],
        'new_book_total': new_book_total,
        'old_book_total': old_book_total,
        'shipping_charge': shipping_charge,
        'weight_charge': weight_charge,
        'total': total,
        'discount': discount,
        'payable': total - discount,
        'paid': 200,
        'refunded': 0,
        'due': total - discount - 200,

        'status': 'order placed',

        'date_created': datetime.now(),
        'date_updated': datetime.now()
    }

    orders.append(new_order)

    return schema.ReadOrder(**new_order)


async def update_order(id: int, payload:schema.UpdateOrder) -> schema.ReadOrder:
    for order in orders:
        if order['id'] == id:
            
            order['books'] = payload.books
            order['shipping_method'] = payload.shipping_method
            order['coupon_code'] = payload.coupon_code
            # order['transaction_ids'] = payload.transaction_ids
            order['date_updated'] = datetime.now()

            return schema.ReadOrder(**order)
    raise HTTPException(status_code=404, detail='Order not found')

async def get_all_orders() -> List[schema.ReadOrder]:
    return orders


async def get_order_by_id(id: int):
    for order in orders:
        if order['id'] == id:
            return order

    return None


async def delete_order(id: int):
    for order in orders:
        if order['id'] == id:
            orders.remove(order)
            return {'msg': 'Order deleted successfully'}

    raise HTTPException(status_code=404, detail='Order not found')


async def search_order(key: str):
    result = []
    for order in orders:
        if key in order['status']:
            result.append(order)

    return result
