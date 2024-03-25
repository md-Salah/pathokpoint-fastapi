from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy import select, func, delete
from typing import Sequence
from uuid import UUID

from app.models.transaction import Transaction
from app.models import PaymentGateway, Order, User

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
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Transaction with transaction id ({}) already exists'.format(payload['transaction_id']))

    payload = await build_relationship(payload, db)

    transaction = Transaction(**payload)
    db.add(transaction)
    await db.commit()
    return transaction


async def delete_transaction(id: UUID, db: AsyncSession) -> None:
    await db.execute(delete(Transaction).where(Transaction.id == id))
    await db.commit()


async def count_transaction(db: AsyncSession) -> int:
    result = await db.execute(select(func.count()).select_from(Transaction))
    return result.scalar_one()


async def build_relationship(payload: dict, db: AsyncSession) -> dict:
    gateway = await db.get(PaymentGateway, payload['gateway'])
    if not gateway:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Payment gateway with id ({}) not found'.format(payload['gateway']))
    payload['gateway'] = gateway

    if payload.get('order'):
        order = await db.get(Order, payload['order'])
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail='Order with id ({}) not found'.format(payload['order']))

    if payload.get('refunded_by'):
        refunded_by = await db.get(User, payload['refunded_by'])
        if not refunded_by:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail='User with id ({}) not found'.format(payload['refunded_by']))
        payload['refunded_by'] = refunded_by
    
    return payload

