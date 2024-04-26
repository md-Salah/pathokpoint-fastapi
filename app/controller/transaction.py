from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy import select, func, delete
from typing import Sequence
from uuid import UUID

from app.models.transaction import Transaction
from app.models import PaymentGateway, Order, User
import app.controller.user as user_service
import app.controller.payment_gateway as gateway_service
from app.controller.exception import not_found_exception, bad_request_exception

query = select(Transaction).options(
    joinedload(Transaction.gateway),
    joinedload(Transaction.order),
    joinedload(Transaction.refunded_by),
)

async def get_transaction_by_id(id: UUID, db: AsyncSession) -> Transaction:
    transaction = await db.scalar(query.filter(Transaction.id == id))
    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Transaction with id ({id}) not found')
    return transaction


async def get_all_transactions(page: int, per_page: int, db: AsyncSession) -> Sequence[Transaction]:
    offset = (page - 1) * per_page
    result = await db.execute(query.offset(offset).limit(per_page))
    return result.scalars().unique().all()


async def create_transaction(payload: dict, db: AsyncSession) -> Transaction:
    if await db.scalar(select(Transaction).filter(Transaction.transaction_id == payload['transaction_id'])):
        raise bad_request_exception(str(payload['transaction_id']), 'Duplicate transaction id')

    transaction = Transaction(**payload)

    # Payment gateway
    gateway = await db.get(PaymentGateway, payload['gateway_id'])
    if not gateway:
        raise not_found_exception(str(payload['gateway_id']), 'Payment gateway not found')
    transaction.gateway = gateway
    
    # Order (optional for now)
    if payload.get('order_id'):
        order = await db.get(Order, payload['order_id'])
        if not order:
            raise not_found_exception(str(payload['order_id']), 'Order not found')
        transaction.order = order

    # Refunded by (optional)
    if payload.get('refunded_by_id'):
        refunded_by = await db.get(User, payload['refunded_by_id'])
        if not refunded_by:
            raise not_found_exception(str(payload['refunded_by_id']), 'Refunded by user not found')
        transaction.refunded_by = refunded_by
    
    db.add(transaction)
    await db.commit()
    return transaction


async def delete_transaction(id: UUID, db: AsyncSession) -> None:
    await db.execute(delete(Transaction).where(Transaction.id == id))
    await db.commit()


async def count_transaction(db: AsyncSession) -> int:
    result = await db.execute(select(func.count()).select_from(Transaction))
    return result.scalar_one()



