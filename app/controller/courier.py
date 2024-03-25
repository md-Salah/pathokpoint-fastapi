from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete, update
from typing import Sequence
from uuid import UUID

from app.models.courier import Courier


async def get_courier_by_id(id: UUID, db: AsyncSession) -> Courier:
    courier = await db.scalar(select(Courier).filter(Courier.id == id))
    if not courier:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Courier with id ({id}) not found')
    return courier


async def get_all_couriers(page: int, per_page: int, db: AsyncSession) -> Sequence[Courier]:
    offset = (page - 1) * per_page
    result = await db.execute(select(Courier).offset(offset).limit(per_page))
    return result.scalars().all()


async def create_courier(payload: dict, db: AsyncSession) -> Courier:
    if await db.scalar(select(Courier).filter(Courier.method_name == payload['method_name'])):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'Courier with method name ({payload["method_name"]}) already exists')

    courier = Courier(**payload)
    db.add(courier)
    await db.commit()
    return courier


async def update_courier(id: UUID, payload: dict, db: AsyncSession) -> Courier:
    courier = await get_courier_by_id(id, db)
    [setattr(courier, key, value)
     for key, value in payload.items()]
    await db.commit()
    return courier


async def delete_courier(id: UUID, db: AsyncSession) -> None:
    await db.execute(delete(Courier).where(Courier.id == id))
    await db.commit()


async def count_courier(db: AsyncSession) -> int:
    result = await db.execute(select(func.count()).select_from(Courier))
    return result.scalar_one()
