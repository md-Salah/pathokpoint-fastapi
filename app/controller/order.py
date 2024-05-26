from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from uuid import UUID
from datetime import datetime
from typing import Sequence, List
from sqlalchemy.orm import joinedload, selectinload

# from app.filter_schema.order import OrderFilter
from app.models import Order, Book, OrderItem, OrderStatus, Transaction
from app.constant.discount_type import DiscountType
from app.constant.orderstatus import Status
import app.controller.coupon as coupon_service
import app.controller.courier as courier_service
import app.controller.user as user_service
from app.models import Address
from app.controller.exception import NotFoundException, BadRequestException, not_found_exception, bad_request_exception

order_query = select(Order).options(
    selectinload(Order.order_items).joinedload(OrderItem.book),
    selectinload(Order.order_status).joinedload(OrderStatus.updated_by),
    selectinload(Order.transactions).joinedload(Transaction.gateway),
)


async def get_order_by_id(id: UUID, db: AsyncSession) -> Order:
    order = await db.scalar(order_query.where(Order.id == id))
    if not order:
        raise NotFoundException('Order not found')

    return order


async def get_all_orders(page: int, per_page: int, db: AsyncSession,
                         # order_filter: OrderFilter,
                         ) -> Sequence[Order]:
    offset = (page - 1) * per_page
    stmt = order_query

    stmt = stmt.offset(offset).limit(per_page)
    result = await db.execute(stmt)
    orders = result.unique().scalars().all()
    return orders


async def count_orders(db: AsyncSession) -> int:
    stmt = select(func.count()).select_from(Order)
    result = await db.scalar(stmt)

    return result or 0


async def create_order(payload: dict, db: AsyncSession) -> Order:
    order = Order()

    # Customer
    if payload.get('customer_id'):
        order.customer = await user_service.get_user_by_id(payload['customer_id'], db)

    # Order Items
    order.order_items = await manage_inventory(payload['order_items'], db)
    order.old_book_total = sum(
        [item.sold_price * item.quantity for item in order.order_items if item.book.is_used])
    order.new_book_total = sum(
        [item.sold_price * item.quantity for item in order.order_items if not item.book.is_used])

    # Shipping
    order.shipping_charge, order.weight_charge = 0, 0
    if payload.get('address_id'):
        weight_kg = sum(
            [item.book.weight_in_gm for item in order.order_items])/1000
        order.shipping_charge, order.weight_charge, order.address, order.courier = await handle_shipping(
            payload['address_id'], payload['courier_id'], weight_kg, db)

    # Coupon & Discount
    order.discount = 0
    if payload.get('coupon_id'):
        order.discount, order.coupon, order.shipping_charge = await apply_coupon(
            payload['coupon_id'], order.order_items.copy(), order.shipping_charge, db)

    # Status
    order.order_status = [OrderStatus(
        status=Status.pending_payment, note='Minimum payment is required to confirm the order')]

    # Payment
    order.transactions = []
    order.paid = 0

    # Created by
    # order.created_by = await user_service.get_user_by_id(payload['created_by'], db)

    # Summary
    order.total = order.new_book_total + order.old_book_total + \
        order.shipping_charge + order.weight_charge
    order.payable = order.total - order.discount
    order.cash_on_delivery = order.payable - order.paid

    db.add(order)
    await db.commit()

    return order


async def update_order(id: UUID, payload: dict, db: AsyncSession) -> Order:
    order = await db.scalar(order_query.options(
                            joinedload(Order.coupon),
                            selectinload(Order.address),
                            joinedload(Order.courier)
                            )
                            .where(Order.id == id))
    if not order:
        raise NotFoundException('Order not found')

    validate_coupon = False
    # Order Items
    if payload.get('order_items'):
        order.order_items = await manage_inventory(payload['order_items'], db, order_id=order.id)
        items = [item for item in order.order_items if item.is_removed is False]
        order.old_book_total = sum(
            [item.sold_price * item.quantity for item in items if item.book.is_used])
        order.new_book_total = sum(
            [item.sold_price * item.quantity for item in items if not item.book.is_used])
        validate_coupon = True

    # Shipping
    if payload.get('address_id'):
        weight_kg = sum([item.book.weight_in_gm for item in items])/1000
        order.shipping_charge, order.weight_charge, order.address, order.courier = await handle_shipping(
            payload['address_id'], payload['courier_id'], weight_kg, db)
        validate_coupon = True

    # Coupon & Discount
    items = [item for item in order.order_items if item.is_removed is False]
    if payload.get('coupon_id'):
        order.discount, order.coupon, order.shipping_charge = await apply_coupon(
            payload['coupon_id'], items, order.shipping_charge, db)
    elif validate_coupon and order.coupon:
        order.discount, order.coupon, order.shipping_charge = await apply_coupon(
            order.coupon.id, items, order.shipping_charge, db)

    # Status
    if payload.get('order_status'):
        if order.order_status[-1].status != payload['order_status']['status']:
            order.order_status.append(
                OrderStatus(
                    **payload['order_status'],
                )
            )

    # Payment
    if payload.get('transactions'):
        order.paid, order.refunded, order.transactions = await validate_payment(order.id, payload['transactions'], db)

    # Summary
    order.total = order.new_book_total + order.old_book_total + \
        order.shipping_charge + order.weight_charge
    order.payable = order.total - order.discount
    order.cash_on_delivery = order.payable - order.paid

    await db.commit()
    return order


async def delete_order(id: UUID, db: AsyncSession) -> None:
    order = await db.get(Order, id)
    if not order:
        raise NotFoundException('Order not found')

    # Restock items
    await manage_inventory([], db, order_id=id)

    await db.delete(order)
    await db.commit()


async def manage_inventory(items_in: list[dict], db: AsyncSession, order_id: UUID | None = None):

    existing_items = {item.book_id: item for item in
                      (await db.scalars(select(OrderItem).options(
                          joinedload(OrderItem.book)
                      ).filter(OrderItem.order_id == order_id)))} if order_id else {}

    book_ids = [item['book_id'] for item in items_in]
    result = await db.scalars(select(Book).filter(Book.id.in_(book_ids)))
    books = {book.id: book for book in result}

    items = []
    for item in items_in:
        book_id = item['book_id']
        book = books.get(book_id)
        if not book:
            raise NotFoundException(str(book_id), 'Book not found')

        _item = existing_items.get(book.id)
        if _item:
            if item['quantity'] > _item.quantity:  # Increase quantity
                await reduce_stock(book, (item['quantity'] - _item.quantity))
            elif item['quantity'] < _item.quantity:
                await restock_item(book, (_item.quantity - item['quantity']))
            _item.quantity = item['quantity']
            _item.is_removed = item.get('is_removed', False)
            _item.note = item.get('note', None)

            items.append(_item)
        else:
            await reduce_stock(book, item['quantity'])
            items.append(OrderItem(
                book=book,
                regular_price=book.regular_price,
                sold_price=book.sale_price,
                quantity=item['quantity'],
                is_removed=item.get('is_removed', False),
                note=item.get('note', None)
            ))

    # Restock removed items
    for book_id, _item in existing_items.items():
        if book_id not in book_ids:
            await restock_item(_item.book, _item.quantity)

    return items


async def apply_coupon(coupon_id: UUID, items: List[OrderItem], shipping_charge: float, db: AsyncSession):
    coupon = await coupon_service.get_coupon_by_id(coupon_id, db)

    if coupon.expiry_date and coupon.expiry_date < datetime.now():
        raise BadRequestException(str(coupon_id), "Coupon '{}' has expired".format(coupon.code))

    if coupon.use_limit and coupon.use_limit <= coupon._use_count:
        raise BadRequestException(str(coupon_id), "Coupon '{}' has reached its limit".format(coupon.code))

    if coupon.use_limit_per_user:
        pass

    # Include items
    for item in items:
        if coupon.include_conditions and item.book.condition not in coupon.include_conditions:
            items.remove(item)
        elif coupon.include_books and item.book not in coupon.include_books:
            items.remove(item)
        elif coupon.include_publishers and (await item.book.awaitable_attrs.publisher) not in coupon.include_publishers:
            items.remove(item)
        elif coupon.include_authors and not any(author in coupon.include_authors for author in (await item.book.awaitable_attrs.authors)):
            items.remove(item)
        elif coupon.include_categories and not any(category in coupon.include_categories for category in (await item.book.awaitable_attrs.categories)):
            items.remove(item)
        elif coupon.include_tags and not any(tag in coupon.include_tags for tag in (await item.book.awaitable_attrs.tags)):
            items.remove(item)

    # Exclude items
    for item in items:
        if item.book in coupon.exclude_books:
            items.remove(item)
        elif coupon.exclude_publishers and (await item.book.awaitable_attrs.publisher) in coupon.exclude_publishers:
            items.remove(item)
        elif coupon.exclude_authors and any(author in coupon.exclude_authors for author in (await item.book.awaitable_attrs.authors)):
            items.remove(item)
        elif coupon.exclude_categories and any(category in coupon.exclude_categories for category in (await item.book.awaitable_attrs.categories)):
            items.remove(item)
        elif coupon.exclude_tags and any(tag in coupon.exclude_tags for tag in (await item.book.awaitable_attrs.tags)):
            items.remove(item)

    old_book_total = sum(
        [item.sold_price * item.quantity for item in items if item.book.is_used])
    new_book_total = sum(
        [item.sold_price * item.quantity for item in items if not item.book.is_used])

    discount = 0
    old_applicable = old_book_total >= coupon.min_spend_old
    if old_applicable and coupon.discount_old:

        if coupon.discount_type == DiscountType.percentage:
            if coupon.max_discount_old:
                discount = min(
                    old_book_total * coupon.discount_old / 100, coupon.max_discount_old)
            else:
                discount = old_book_total * coupon.discount_old / 100

        elif coupon.discount_type == DiscountType.fixed_amount:
            discount = coupon.discount_old

        elif coupon.discount_type == DiscountType.flat_rate:
            flat_price = sum([min(item.sold_price, coupon.discount_old)
                             * item.quantity for item in items if item.book.is_used])
            discount = old_book_total - flat_price

    new_applicable = new_book_total >= coupon.min_spend_new
    if new_applicable and coupon.discount_new:
        if coupon.discount_type == DiscountType.percentage:
            if coupon.max_discount_new:
                discount += min((new_book_total * coupon.discount_new / 100),
                                coupon.max_discount_new)  # x% off upto y Tk
            else:
                discount += new_book_total * coupon.discount_new / 100  # x% off
        elif coupon.discount_type == DiscountType.fixed_amount:
            discount += coupon.discount_new    # 60 Tk discount
        elif coupon.discount_type == DiscountType.flat_rate:
            flat_price = sum([min(item.sold_price, coupon.discount_new)
                             * item.quantity for item in items if not item.book.is_used])
            discount += new_book_total - flat_price   # Stock clearance, 99 Tk flat rate
    discount = round(discount, 2)
    coupon._discount_applied_new += discount # consider old also


    if coupon.max_shipping_charge and shipping_charge > coupon.max_shipping_charge:
        if new_applicable:
            coupon._discount_applied_new += (shipping_charge - coupon.max_shipping_charge)
            shipping_charge = coupon.max_shipping_charge
        elif old_applicable:
            coupon._discount_applied_new += (shipping_charge - coupon.max_shipping_charge)
            shipping_charge = coupon.max_shipping_charge

    coupon._use_count += 1

    return discount, coupon, shipping_charge


async def validate_payment(order_id: UUID, trans_ids: List[UUID], db: AsyncSession):
    transactions = list((await db.scalars(select(Transaction).options(
        joinedload(Transaction.gateway)
    ).filter(Transaction.id.in_(trans_ids)))).all())
    trans_map = {transaction.id: transaction for transaction in transactions}

    for id in trans_ids:
        trans = trans_map.get(id)
        if not trans:
            raise not_found_exception(str(id), 'Transaction not found')
        elif trans.order_id != order_id:
            raise bad_request_exception(
                str(id), 'Transaction does not belong to this order')

    paid = sum(
        [transaction.amount for transaction in transactions if not transaction.is_refund])
    refunded = sum(
        [transaction.amount for transaction in transactions if transaction.is_refund])

    return paid, refunded, transactions


async def handle_shipping(address_id: UUID, courier_id: UUID, weight_kg: float, db: AsyncSession):
    address = await db.get(Address, address_id)
    if not address:
        raise not_found_exception(str(address_id), 'Address not found')
    courier = await courier_service.get_courier_by_id(courier_id, db)

    if courier.include_country and address.country not in courier.include_country:
        raise bad_request_exception(str(courier_id), "'{}' does not deliver to {}".format(
            courier.method_name, address.country.value))
    if courier.include_city and address.city not in courier.include_city:
        raise bad_request_exception(str(courier_id), "'{}' does not deliver to {}".format(
            courier.method_name, address.city.value))
    if courier.exclude_city and address.city in courier.exclude_city:
        raise bad_request_exception(str(courier_id), "'{}' does not deliver to {}".format(
            courier.method_name, address.city.value))

    shipping_charge = courier.base_charge
    weight_charge = round((courier.weight_charge_per_kg * weight_kg), 2)

    return shipping_charge, weight_charge, address, courier


async def reduce_stock(book: Book, quantity: int):
    if quantity < 1:
        raise ValueError("Quantity must be greater than 0")

    if not book.in_stock:
        raise bad_request_exception(
            str(book.id), "Book '{}' is out of stock".format(book.name))

    if book.manage_stock:
        if book.quantity < quantity:
            raise bad_request_exception(str(
                book.id), "Book '{}' has insufficent stock, only {} left.".format(book.name, book.quantity))
        book.quantity -= quantity
        book.in_stock = book.quantity > 0


async def restock_item(book: Book, quantity: int):
    if quantity < 1:
        raise ValueError("Quantity must be greater than 0")

    if book.manage_stock:
        book.quantity += quantity
        book.in_stock = True
