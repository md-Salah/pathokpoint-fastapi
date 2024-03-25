from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete, update
from typing import Sequence
from uuid import UUID

from app.models.payment_gateway import PaymentGateway


async def get_payment_gateway_by_id(id: UUID, db: AsyncSession) -> PaymentGateway:
    payment_gateway = await db.scalar(select(PaymentGateway).filter(PaymentGateway.id == id))
    if not payment_gateway:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'PaymentGateway with id ({id}) not found')
    return payment_gateway


async def get_all_payment_gateways(page: int, per_page: int, db: AsyncSession) -> Sequence[PaymentGateway]:
    offset = (page - 1) * per_page
    result = await db.execute(select(PaymentGateway).offset(offset).limit(per_page))
    return result.scalars().all()


async def create_payment_gateway(payload: dict, db: AsyncSession) -> PaymentGateway:
    if await db.scalar(select(PaymentGateway).filter(func.lower(PaymentGateway.name) == payload['name'].lower())):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='PaymentGateway with method name ({}) already exists'.format(payload['name']))

    payment_gateway = PaymentGateway(**payload)
    db.add(payment_gateway)
    await db.commit()
    return payment_gateway


async def update_payment_gateway(id: UUID, payload: dict, db: AsyncSession) -> PaymentGateway:
    payment_gateway = await get_payment_gateway_by_id(id, db)
    [setattr(payment_gateway, key, value)
     for key, value in payload.items()]
    await db.commit()
    return payment_gateway


async def delete_payment_gateway(id: UUID, db: AsyncSession) -> None:
    await db.execute(delete(PaymentGateway).where(PaymentGateway.id == id))
    await db.commit()


async def count_payment_gateway(db: AsyncSession) -> int:
    result = await db.execute(select(func.count()).select_from(PaymentGateway))
    return result.scalar_one()
