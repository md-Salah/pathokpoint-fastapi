from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Sequence
from uuid import UUID

from app.models.address import Address


async def get_address_by_id(id: UUID, db: AsyncSession) -> Address:
    address = await db.scalar(select(Address).filter(Address.id == id))
    if not address:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Address with id ({id}) not found')
    return address


async def get_all_addresss(page: int, per_page: int, db: AsyncSession) -> Sequence[Address]:
    offset = (page - 1) * per_page
    result = await db.execute(select(Address).offset(offset).limit(per_page))
    return result.scalars().all()


async def create_address(payload: dict, db: AsyncSession) -> Address:
    address = Address(**payload)
    db.add(address)
    await db.commit()
    return address


async def update_address(id: UUID, payload: dict, db: AsyncSession) -> Address:
    address = await get_address_by_id(id, db)
    [setattr(address, key, value)
     for key, value in payload.items()]
    await db.commit()
    return address


async def delete_address(id: UUID, db: AsyncSession) -> None:
    address = await get_address_by_id(id, db)
    await db.delete(address)
    await db.commit()


async def count_address(db: AsyncSession) -> int:
    result = await db.execute(select(func.count()).select_from(Address))
    return result.scalar_one()
