from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy import select, func
from typing import Sequence
from uuid import UUID
import logging

from app.models.transaction import Transaction
from app.models import PaymentGateway, Order, User
from app.controller.exception import NotFoundException, ConflictException, ForbiddenException
from app.filter_schema.transaction import TransactionFilter
from app.constant.role import Role

logger = logging.getLogger(__name__)

query = select(Transaction).options(
    joinedload(Transaction.gateway),
    selectinload(Transaction.order),
    selectinload(Transaction.refunded_by),
)


async def get_transaction_by_id(id: UUID, customer_id: UUID, role: str, db: AsyncSession) -> Transaction:
    transaction = await db.scalar(query.filter(Transaction.id == id))
    if not transaction:
        raise NotFoundException('Transaction not found', str(id))

    if transaction.customer_id == customer_id:
        return transaction
    elif role == Role.admin.value:
        return transaction

    raise ForbiddenException('Transaction does not belong to you')


async def get_all_transactions(filter: TransactionFilter, page: int, per_page: int, db: AsyncSession) -> Sequence[Transaction]:
    query = select(Transaction).options(
        joinedload(Transaction.gateway),
        joinedload(Transaction.order),
        joinedload(Transaction.refunded_by),
    )
    query = filter.filter(query)

    offset = (page - 1) * per_page
    result = await db.execute(query.offset(offset).limit(per_page))
    return result.scalars().unique().all()


async def count_transaction(filter: TransactionFilter, db: AsyncSession) -> int:
    stmt = select(func.count()).select_from(Transaction)
    stmt = filter.filter(stmt)
    result = await db.execute(stmt)
    return result.scalar_one()


async def create_transaction(payload: dict, db: AsyncSession) -> Transaction:
    _transaction = await db.scalar(select(Transaction).filter(Transaction.transaction_id == payload['transaction_id']))
    if _transaction:
        raise ConflictException('Transaction already exists')

    gateway = await db.get(PaymentGateway, payload['gateway_id'])
    if not gateway:
        raise NotFoundException('Invalid payment gateway',
                                str(payload['gateway_id']))
    payload['gateway'] = gateway

    order = await db.get(Order, payload['order_id'])
    if not order:
        raise NotFoundException('Invalid order id', str(payload['order_id']))
    payload['order'] = order
    if order.customer_id and order.customer_id != payload['customer_id']:
        raise ConflictException('Order does not belong to the user')

    if payload['customer_id']:
        user = await db.get(User, payload['customer_id'])
        if not user:
            raise NotFoundException(
                'User not found', str(payload['customer_id']))
        payload['user'] = user

    if 'refunded_by_id' in payload:
        refunded_by = await db.get(User, payload['refunded_by_id'])
        if not refunded_by:
            raise NotFoundException(
                'Admin not found for the refund', str(payload['refunded_by_id']))
        payload['refunded_by'] = refunded_by

    logger.debug(f'Creating transaction: {payload}')
    transaction = Transaction(**payload)

    db.add(transaction)
    await db.commit()
    logger.info(f'Transaction created: {transaction}')
    return transaction


async def delete_transaction(id: UUID, db: AsyncSession) -> None:
    transaction = await db.get(Transaction, id)
    if not transaction:
        raise NotFoundException('Transaction not found', str(id))
    await db.delete(transaction)
    await db.commit()
    logger.info(f'Transaction deleted: {transaction}')
