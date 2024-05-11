from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Sequence
from uuid import UUID
import logging

from app.models.address import Address
from app.models.user import User
from app.controller.exception import NotFoundException, ForbiddenException
from app.constant.role import Role

logger = logging.getLogger(__name__)


async def get_address_by_id(id: UUID, user_id: UUID, role: str, db: AsyncSession) -> Address:
    address = await db.scalar(select(Address).filter(Address.id == id))
    if not address:
        raise NotFoundException('Address not found')
    if address.user_id == user_id or role == Role.admin.value:
        return address
    raise ForbiddenException('You are not allowed to access this address')


async def get_all_addresss(user_id: UUID, page: int, per_page: int, db: AsyncSession) -> Sequence[Address]:
    user = await db.get(User, user_id)
    if not user:
        raise NotFoundException('User not found')

    offset = (page - 1) * per_page
    result = await db.execute(select(Address).where(Address.user == user).offset(offset).limit(per_page))
    return result.scalars().all()


async def count_address(user_id: UUID, db: AsyncSession) -> int:
    result = await db.execute(select(func.count()).where(Address.user_id == user_id).select_from(Address))
    return result.scalar_one()


async def create_address(user_id: UUID, payload: dict, db: AsyncSession) -> Address:
    user = await db.get(User, user_id)
    if not user:
        raise NotFoundException('User not found')

    logger.debug(f'Creating address for user {user} with payload {payload}')
    address = Address(**payload)
    address.user = user
    db.add(address)
    await db.commit()
    logger.info(f'Address {address} created, user {user}')
    return address


async def update_address(id: UUID, user_id: UUID, payload: dict, db: AsyncSession) -> Address:
    address = await db.get(Address, id)
    if not address:
        raise NotFoundException('Address not found')
    if address.user_id != user_id:
        raise ForbiddenException('You are not allowed to update this address')

    logger.debug(f'Updating address {address} with payload {payload}')
    [setattr(address, key, value)
     for key, value in payload.items()]
    await db.commit()
    logger.info(f'Address {address} updated')
    return address


async def delete_address(id: UUID, user_id: UUID, role: str, db: AsyncSession) -> None:
    address = await db.get(Address, id)
    if not address:
        raise NotFoundException('Address not found')

    if address.user_id == user_id or role == Role.admin.value:
        await db.delete(address)
        await db.commit()
        logger.info(f'Address {address} deleted')
        return

    logger.debug(f'User {user_id} is not allowed to delete address {address}')
    raise ForbiddenException('You are not allowed to delete this address')
