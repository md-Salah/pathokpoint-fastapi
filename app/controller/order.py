from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from uuid import UUID, uuid4
from datetime import datetime, timezone
from typing import Sequence, List, Tuple, Any
from sqlalchemy.orm import selectinload, aliased
import logging

from app.filter_schema.order import OrderFilter, OrderFilterCustomer
from app.models import Order, Book, OrderItem, OrderStatus, Transaction, User, Courier, Coupon
from app.constant.discount_type import DiscountType
from app.constant.orderstatus import Status
import app.controller.coupon as coupon_service
import app.controller.transaction as transaction_service
from app.controller.courier import get_courier_by_id
from app.models import Address
from app.controller.exception import NotFoundException, BadRequestException, ServerErrorException

logger = logging.getLogger(__name__)

order_query = select(Order).options(
    selectinload(Order.order_items).selectinload(OrderItem.book).selectinload(Book.authors),
    selectinload(Order.order_items).selectinload(OrderItem.book).selectinload(Book.images),
    selectinload(Order.order_status).selectinload(OrderStatus.updated_by),
    selectinload(Order.transactions).selectinload(Transaction.gateway),
    selectinload(Order.transactions).selectinload(Transaction.refunded_by),
    selectinload(Order.address),
    selectinload(Order.courier),
    selectinload(Order.coupon),
    selectinload(Order.customer),
)


async def get_order_by_id(id: UUID, db: AsyncSession) -> Order:
    order = await db.scalar(order_query.where(Order.id == id))
    if not order:
        raise NotFoundException('Order not found')
    return order


async def get_order_by_invoice(invoice: int | str, db: AsyncSession) -> Order:
    if isinstance(invoice, str):
        try:
            invoice = int(invoice)
        except ValueError:
            raise BadRequestException('Invalid invoice number')
    order = await db.scalar(order_query.where(Order.invoice == invoice))
    if not order:
        raise NotFoundException('Order not found')
    return order


async def get_all_orders(filter: OrderFilter, page: int, per_page: int, db: AsyncSession) -> Tuple[Sequence[Order], int]:
    offset = (page - 1) * per_page
    query = order_query

    if filter.order_status.status:
        os2 = aliased(OrderStatus)
        subquery = select(func.max(os2.created_at)).where(
            os2.order_id == Order.id).scalar_subquery()
        query = query.filter(OrderStatus.created_at == subquery,
                             OrderStatus.status == filter.order_status.status)
        filter.order_status.pop('status')
    query = query.join(Order.order_status)

    if any([filter.coupon.id, filter.coupon.code]):
        query = query.outerjoin(Order.coupon)
    if any([filter.customer.id, filter.customer.username, filter.customer.email, filter.customer.phone_number]):
        query = query.outerjoin(Order.customer)
    if any([filter.address.id, filter.address.phone_number, filter.address.thana, filter.address.city, filter.address.country]):
        query = query.outerjoin(Order.address)
    if any([filter.courier.id__in, filter.courier.method_name__in, filter.courier.company_name, filter.courier.allow_cash_on_delivery]):
        query = query.outerjoin(Order.courier)

    query = filter.filter(query)
    stmt = filter.sort(query)
    stmt = stmt.offset(offset).limit(per_page)
    result = await db.execute(stmt)
    orders = result.unique().scalars().all()

    # Count
    stmt = select(func.count()).select_from(query.subquery())
    count = (await db.scalar(stmt)) or 0
    return orders, count


async def get_my_orders(filter: OrderFilterCustomer, customer_id: UUID, page: int, per_page: int, db: AsyncSession) -> Tuple[Sequence[Order], int]:
    offset = (page - 1) * per_page
    query = order_query.filter(Order.customer_id == customer_id)

    if filter.order_status.status:
        os2 = aliased(OrderStatus)
        subquery = select(func.max(os2.created_at)).where(
            os2.order_id == Order.id).scalar_subquery()
        query = query.filter(OrderStatus.created_at == subquery,
                             OrderStatus.status == filter.order_status.status)
        filter.order_status.pop('status')

    query = query.join(Order.order_status)
    query = filter.filter(query)
    stmt = filter.sort(query)
    stmt = stmt.offset(offset).limit(per_page)
    result = await db.execute(stmt)
    orders = result.unique().scalars().all()

    # Count
    stmt = select(func.count()).select_from(query.subquery())
    count = (await db.scalar(stmt)) or 0
    return orders, count


async def create_order(payload: dict[str, Any], db: AsyncSession, commit: bool = True, order_id: UUID | None = None) -> Order:
    order = Order()
    order.id = order_id or uuid4()
    order.is_full_paid = payload['is_full_paid']

    if payload.get('customer_id'):
        customer = await db.get(User, payload['customer_id'])
        if not customer:
            raise NotFoundException('Customer not found')
        order.customer = customer

    # Order Items
    if (len(payload['order_items']) < 1):
        raise BadRequestException('Order must have at least one item')
    (
        order.order_items,
        order.old_book_total,
        order.new_book_total,
        order.cost_of_good_old,
        order.cost_of_good_new
    ) = await manage_inventory(payload['order_items'], db)

    # Shipping
    order.shipping_charge, order.weight_charge = 0, 0
    weight_kg = sum(
        [item.book.weight_in_gm for item in order.order_items])/1000
    if payload.get('address'):
        order.address = Address(**payload['address'])
        (
            order.shipping_charge,
            order.weight_charge,
            _,
            order.courier
        ) = await handle_shipping(
            order.address, payload['courier_id'], weight_kg, order.is_full_paid, db)
    elif payload.get('address_id'):
        (
            order.shipping_charge,
            order.weight_charge,
            order.address,
            order.courier
        ) = await handle_shipping(
            payload['address_id'], payload['courier_id'], weight_kg, order.is_full_paid, db)
    if (order.courier):
        order.weight_charge += await additional_weight_charge(order.order_items, order.courier.weight_charge_per_kg)

    # Coupon & Discount
    order.discount = 0
    if payload.get('coupon_code'):
        coupon = await coupon_service.get_coupon_by_code(
            payload['coupon_code'], db)
        order.coupon, order.discount, order.shipping_charge = await apply_coupon(
            coupon, order.order_items, order.shipping_charge, db, payload.get('customer_id'), payload.get('courier_id'))
    elif payload.get('coupon_id'):
        order.coupon, order.discount, order.shipping_charge = await apply_coupon(
            payload['coupon_id'], order.order_items, order.shipping_charge, db, payload.get('customer_id'), payload.get('courier_id'))

    # Paid
    order.transactions = []
    order.paid = 0
    if payload.get('transactions'):
        for transaction in payload['transactions']:
            transaction['customer'] = order.customer
            order.transactions.append(
                await transaction_service.validate_transaction(transaction, db)
            )
            order.paid += transaction['amount']

    # Status
    if order.paid > 0:
        order.order_status = [OrderStatus(status=Status.processing)]
    else:
        order.order_status = [OrderStatus(
            status=Status.pending, note='Minimum payment is required to confirm the order')]

    # Summary
    order.total = order.new_book_total + order.old_book_total + \
        order.shipping_charge + order.weight_charge
    order.net_amount = order.total - order.discount
    order.due = max(0, order.net_amount - order.paid)

    # Profit
    order.additional_cost = 0
    order.shipping_cost = order.shipping_charge + order.weight_charge
    order.gross_profit = order.net_amount - order.cost_of_good_new - \
        order.cost_of_good_old - order.shipping_cost - order.additional_cost

    db.add(order)
    if commit:
        await db.commit()
        logger.info('Order created: {}'.format(order))
    else:
        await db.flush()
        
    return order


async def update_order(id: UUID, payload: dict[str, Any], db: AsyncSession) -> Order:
    logger.debug(f'Updating order with payload: {payload}')
    order = await db.scalar(order_query.where(Order.id == id))
    if not order:
        raise NotFoundException('Order not found')

    # Order Items
    if payload.get('order_items'):
        (
            order.order_items,
            order.old_book_total,
            order.new_book_total,
            order.cost_of_good_old,
            order.cost_of_good_new
        ) = await manage_inventory(payload['order_items'], db, order_id=order.id)

        if order.coupon_id:
            (
                order.coupon,
                order.discount,
                order.shipping_charge
            ) = await apply_coupon(
                order.coupon.id,
                order.order_items,
                order.shipping_charge,
                db,
                order.customer_id,
                order.courier_id,
                False
            )
        logger.debug('Updated order items: {}'.format(order.order_items))

        order.total = order.new_book_total + order.old_book_total + \
            order.shipping_charge + order.weight_charge
        order.net_amount = order.total - order.discount
        order.due = max(0, order.net_amount - order.paid)
        order.gross_profit = order.net_amount - order.cost_of_good_new - \
            order.cost_of_good_old - order.shipping_cost - order.additional_cost

    # Status
    if payload.get('order_status'):
        logger.debug('Current status: {}'.format(order.order_status))
        if order.order_status[-1].status != payload['order_status']['status']:
            order.order_status.append(
                OrderStatus(
                    **payload['order_status'],
                )
            )

    # Payment
    if payload.get('transaction'):
        transaction = payload.pop('transaction')
        transaction['is_manual'] = True  # Manual transaction by admin
        transaction['customer'] = order.customer
        order.transactions.append(
            await transaction_service.validate_transaction(transaction, db)
        )
        order.paid += transaction['amount']
        order.due = max(0, order.net_amount - order.paid)

    if payload.get('discount'):
        order.discount = payload['discount']
        order.net_amount = order.total - order.discount
        order.due = max(0, order.net_amount - order.paid)

    if payload.get('tracking_id'):
        order.tracking_id = payload['tracking_id']

    if payload.get('shipping_cost'):
        order.shipping_cost = payload['shipping_cost']
        order.cod_receivable = 0 if order.is_full_paid else (
            order.due - order.shipping_cost)

    if payload.get('cod_received'):
        order.cod_received = payload['cod_received']

    if payload.get('cost_of_good_new'):
        order.cost_of_good_new = payload['cost_of_good_new']
        order.gross_profit = order.net_amount - order.cost_of_good_new - \
            order.cost_of_good_old - order.additional_cost

    if payload.get('additional_cost'):
        order.additional_cost = payload['additional_cost']
        order.gross_profit = order.net_amount - order.cost_of_good_new - \
            order.cost_of_good_old - order.additional_cost

    if payload.get('customer_id'):
        customer = await db.get(User, payload['customer_id'])
        if not customer:
            raise NotFoundException('Customer not found')
        order.customer = customer

    await db.commit()
    logger.info('Order updated: {}'.format(order))
    return order


async def delete_order(id: UUID, restock: bool, db: AsyncSession) -> None:
    order = await db.get(Order, id)
    if not order:
        raise NotFoundException('Order not found')

    if restock:
        for item in order.order_items:
            book = await item.awaitable_attrs.book
            await restock_item(book, item.quantity)
            
    for trx in (await order.awaitable_attrs.transactions):
        logger.info('Deleting transaction: {}'.format(trx))
        await db.delete(trx)

    logger.info('Deleting order: {}'.format(order))
    await db.delete(order)
    await db.commit()


async def manage_inventory(items_in: list[dict], db: AsyncSession, order_id: UUID | None = None) -> Tuple[list[OrderItem], float, float, float, float]:
    book_ids = [item['book_id'] for item in items_in]
    query = select(Book).options(selectinload(Book.authors), selectinload(Book.images))
    books = {book.id: book for book in (await db.scalars(query.filter(Book.id.in_(book_ids))))}

    existing_items = {item.book_id: item for item in
                      (await db.scalars(select(OrderItem).options(
                          selectinload(OrderItem.book)
                      ).filter(OrderItem.order_id == order_id)))} if order_id else {}

    items: list[OrderItem] = []
    for item in items_in:
        book_id = item['book_id']
        book = books.get(book_id)
        if not book:
            raise NotFoundException('Book not found', str(book_id))

        _item = existing_items.get(book.id)  # applicable for update order
        if _item:
            if item['quantity'] > _item.quantity:  # Asking more quantity
                await reduce_stock(book, (item['quantity'] - _item.quantity))
            elif item['quantity'] < _item.quantity:
                await restock_item(book, (_item.quantity - item['quantity']))
            _item.quantity = item['quantity']
            items.append(_item)
        else:
            await reduce_stock(book, item['quantity'])
            items.append(OrderItem(
                book_id=book.id,
                book=book,
                regular_price=book.regular_price,
                sold_price=book.sale_price,
                quantity=item['quantity'],
            ))

    # Restock removed items
    for book_id, _item in existing_items.items():
        if book_id not in book_ids:
            await restock_item(_item.book, _item.quantity)

    # Sum
    old_book_total, new_book_total, cog_old, cog_new = 0, 0, 0, 0
    for item in items:
        if item.book.is_used:
            old_book_total += item.sold_price * item.quantity
            cog_old += item.book.cost * item.quantity
        else:
            new_book_total += item.sold_price * item.quantity
            cog_new += item.book.cost * item.quantity

    logger.debug("Order items: {}, Old: {}, New: {}".format(items, old_book_total, new_book_total))
    return items, old_book_total, new_book_total, cog_old, cog_new


async def apply_coupon(coupon_id: UUID | Coupon,
                       order_items: List[OrderItem],
                       shipping_charge: float,
                       db: AsyncSession,
                       customer_id: UUID | None = None,
                       courier_id: UUID | None = None,
                       new_order: bool = True) -> Tuple[Coupon, float, float]:
    items = order_items.copy()
    coupon = coupon_id if isinstance(coupon_id, Coupon) else await coupon_service.get_coupon_by_id(coupon_id, db)

    if new_order:
        if not coupon.is_active:
            raise BadRequestException(
                "Coupon '{}' is disabled".format(coupon.code))

        if coupon.expiry_date and coupon.expiry_date < datetime.now(timezone.utc):
            raise BadRequestException("Coupon '{}' has expired".format(coupon.code))

        if coupon.use_limit:
            use_count = await db.scalar(select(func.count(Order.id)).where(Order.coupon_id == coupon.id))
            use_count = use_count or 0
            if use_count >= coupon.use_limit:
                raise BadRequestException(
                    "Coupon '{}' has reached its limit".format(coupon.code))

        if coupon.use_limit_per_user:
            if not customer_id:
                raise BadRequestException("Please login to use this coupon")
            use_count = await db.scalar(select(func.count(Order.id)).where(Order.coupon_id == coupon.id, Order.customer_id == customer_id))
            use_count = use_count or 0
            if use_count >= coupon.use_limit_per_user:
                raise BadRequestException(
                    "You have reached the limit of using coupon '{}'".format(coupon.code))

        if coupon.user_id and coupon.user_id != customer_id:
            raise BadRequestException(
                "Coupon '{}' is not applicable for you".format(coupon.code))

    if courier_id and coupon.exclude_couriers:
        courier = await get_courier_by_id(courier_id, db)
        if courier in coupon.exclude_couriers:
            raise BadRequestException(
                "Coupon '{}' is not applicable with '{}'".format(coupon.code, courier.method_name))

    # Include items
    for item in items:
        if coupon.include_conditions and item.book.condition not in coupon.include_conditions:
            items.remove(item)
        if coupon.include_books and item.book not in coupon.include_books:
            items.remove(item)
        if coupon.include_publishers and (await item.book.awaitable_attrs.publisher) not in coupon.include_publishers:
            items.remove(item)
        if coupon.include_authors and not any(author in coupon.include_authors for author in (await item.book.awaitable_attrs.authors)):
            items.remove(item)
        if coupon.include_categories and not any(category in coupon.include_categories for category in (await item.book.awaitable_attrs.categories)):
            items.remove(item)
        if coupon.include_tags and not any(tag in coupon.include_tags for tag in (await item.book.awaitable_attrs.tags)):
            items.remove(item)

    # Exclude items
    for item in items:
        if item.book in coupon.exclude_books:
            items.remove(item)
        if coupon.exclude_publishers and (await item.book.awaitable_attrs.publisher) in coupon.exclude_publishers:
            items.remove(item)
        if coupon.exclude_authors and any(author in coupon.exclude_authors for author in (await item.book.awaitable_attrs.authors)):
            items.remove(item)
        if coupon.exclude_categories and any(category in coupon.exclude_categories for category in (await item.book.awaitable_attrs.categories)):
            items.remove(item)
        if coupon.exclude_tags and any(tag in coupon.exclude_tags for tag in (await item.book.awaitable_attrs.tags)):
            items.remove(item)

    old_book_total = sum(
        [item.sold_price * item.quantity for item in items if item.book.is_used])
    new_book_total = sum(
        [item.sold_price * item.quantity for item in items if not item.book.is_used])
    logger.debug('Applying coupon, Old book total: {}, New book total: {}'.format(
        old_book_total, new_book_total))

    discount_old = 0
    if coupon.discount_old and old_book_total >= coupon.min_spend_old:
        if coupon.discount_type == DiscountType.percentage:
            discount_old = old_book_total * coupon.discount_old / 100
            discount_old = min(
                discount_old, coupon.max_discount_old) if coupon.max_discount_old else discount_old
        elif coupon.discount_type == DiscountType.fixed_amount:
            discount_old = coupon.discount_old

    discount_new = 0
    if coupon.discount_new and new_book_total >= coupon.min_spend_new:
        if coupon.discount_type == DiscountType.percentage:
            discount_new = new_book_total * coupon.discount_new / 100
            discount_new = min(
                discount_new, coupon.max_discount_new) if coupon.max_discount_new else discount_new
        elif coupon.discount_type == DiscountType.fixed_amount:
            discount_new = coupon.discount_new

    if old_book_total >= coupon.min_spend_old or new_book_total >= coupon.min_spend_new:
        if coupon.max_shipping_charge:
            shipping_charge = min(shipping_charge, coupon.max_shipping_charge)
    elif coupon.discount_old and coupon.discount_new:
        raise BadRequestException('Please buy more {}৳ old or {}৳ new book to use this coupon'.format(
            coupon.min_spend_old - old_book_total, coupon.min_spend_new - new_book_total))
    elif coupon.discount_old:
        raise BadRequestException('Please buy more {}৳ old book to use this coupon'.format(
            coupon.min_spend_old - old_book_total))
    elif coupon.discount_new:
        raise BadRequestException('Please buy more {}৳ new book to use this coupon'.format(
            coupon.min_spend_new - new_book_total))
    else:
        raise BadRequestException('Please buy more {}৳ old or {}৳ new book to use this coupon'.format(
            coupon.min_spend_old - old_book_total, coupon.min_spend_new - new_book_total))

    discount = round(discount_old + discount_new)
    return coupon, discount, shipping_charge


async def handle_shipping(address_id: UUID | Address, courier_id: UUID, weight_kg: float, is_full_paid: bool, db: AsyncSession) -> Tuple[float, float, Address, Courier]:
    if isinstance(address_id, Address):
        address = address_id
    else:
        address = await db.get(Address, address_id)
        if not address:
            raise NotFoundException('Address not found')

    courier = await db.get(Courier, courier_id)
    if not courier:
        raise NotFoundException('Courier not found')
    
    if not is_full_paid and not courier.allow_cash_on_delivery:
        raise BadRequestException("'{}' does not allow cash on delivery".format(courier.method_name))

    if courier.include_country and (address.country not in courier.include_country):
        raise BadRequestException("'{}' does not deliver to {}".format(
            courier.method_name, address.country.value))
    if courier.include_city and (address.city not in courier.include_city):
        raise BadRequestException("'{}' does not deliver to {}".format(
            courier.method_name, address.city.value))
    if courier.exclude_city and (address.city in courier.exclude_city):
        raise BadRequestException("'{}' does not deliver to {}".format(
            courier.method_name, address.city.value))

    shipping_charge = courier.base_charge
    weight_charge = 0 if (weight_kg < 1) else round(
        (courier.weight_charge_per_kg * weight_kg), 2)

    return shipping_charge, weight_charge, address, courier


async def reduce_stock(book: Book, quantity: int) -> None:
    if quantity < 1:
        logger.error('Cannot reduce stock by %s', quantity)
        raise ServerErrorException('Something went wrong.')

    if not book.in_stock:
        raise BadRequestException(
            "Book '{}' is out of stock".format(book.name), str(book.id))

    if book.manage_stock:
        if book.quantity < quantity:
            raise BadRequestException(
                "Book '{}' has insufficient stock".format(book.name), str(book.id))
        book.quantity -= quantity
        book.in_stock = book.quantity > 0


async def restock_item(book: Book, quantity: int) -> None:
    if quantity < 1:
        logger.error('Cannot restock by %s', quantity)
        raise ServerErrorException('Something went wrong.')

    if book.manage_stock:
        book.quantity += quantity
        book.in_stock = True


async def additional_weight_charge(items: List[OrderItem], weight_charge_per_kg) -> float:
    sub_total = sum(
        [item.sold_price * item.quantity for item in items if item.book.weight_in_gm == 0])
    return (sub_total//1000) * weight_charge_per_kg

