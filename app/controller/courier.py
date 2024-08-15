from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, literal_column
from typing import Sequence
from uuid import UUID
import logging

from app.models.courier import Courier
from app.controller.exception import NotFoundException, ConflictException
from app.filter_schema.courier import CourierFilter

logger = logging.getLogger(__name__)


async def get_courier_by_id(id: UUID, db: AsyncSession) -> Courier:
    courier = await db.scalar(select(Courier).filter(Courier.id == id))
    if not courier:
        raise NotFoundException('Courier not found')
    return courier


async def get_all_couriers(filter: CourierFilter, page: int, per_page: int, db: AsyncSession) -> Sequence[Courier]:
    offset = (page - 1) * per_page

    if (filter.city is not None):
        stmt = select(Courier).filter(
            or_(
                Courier.include_city == [],
                Courier.include_city.any(literal_column(f"'{filter.city.value}'"))
            ),
            ~Courier.exclude_city.any(literal_column(f"'{filter.city.value}'"))
        )
        filter.city = None
    else:
        stmt = select(Courier)

    stmt = filter.filter(stmt)
    stmt = stmt.offset(offset).limit(per_page)
    result = await db.execute(stmt)
    return result.scalars().all()


async def count_courier(filter: CourierFilter, db: AsyncSession) -> int:
    stmt = select(func.count(Courier.id))
    stmt = filter.filter(stmt)
    result = await db.execute(stmt)
    return result.scalar_one()


async def create_courier(payload: dict, db: AsyncSession) -> Courier:
    _courier = await db.scalar(select(Courier).filter(Courier.method_name == payload['method_name']))
    if _courier:
        raise ConflictException('Courier with name {} already exists'.format(
            _courier.method_name), str(_courier.id))

    logger.debug('Creating courier with payload: %s', payload)
    courier = Courier(**payload)
    db.add(courier)
    await db.commit()

    logger.info(f'Courier created {courier}')
    return courier


async def update_courier(id: UUID, payload: dict, db: AsyncSession) -> Courier:
    courier = await get_courier_by_id(id, db)

    logger.debug('Updating courier with payload: %s', payload)
    [setattr(courier, key, value)
     for key, value in payload.items()]
    await db.commit()

    logger.info(f'Courier updated {courier}')
    return courier


async def delete_courier(id: UUID, db: AsyncSession) -> None:
    courier = await db.get(Courier, id)
    if not courier:
        raise NotFoundException('Courier not found')
    await db.delete(courier)
    await db.commit()

    logger.info(f'Courier deleted {courier}')
