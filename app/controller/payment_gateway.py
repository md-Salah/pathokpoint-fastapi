from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Sequence
from uuid import UUID
import logging

from app.models.payment_gateway import PaymentGateway
from app.controller.exception import NotFoundException, ConflictException

logger = logging.getLogger(__name__)


async def get_payment_gateway_by_id(id: UUID, db: AsyncSession) -> PaymentGateway:
    payment_gateway = await db.scalar(select(PaymentGateway).filter(PaymentGateway.id == id))
    if not payment_gateway:
        raise NotFoundException('Payment Gateway not found')
    return payment_gateway


async def get_all_payment_gateways(page: int, per_page: int, db: AsyncSession) -> Sequence[PaymentGateway]:
    offset = (page - 1) * per_page
    result = await db.execute(select(PaymentGateway).offset(offset).limit(per_page))
    return result.scalars().all()


async def gateways_for_customer(db: AsyncSession) -> Sequence[PaymentGateway]:
    result = await db.execute(select(PaymentGateway).filter(PaymentGateway.is_admin_only.is_(False)).order_by(PaymentGateway.is_disabled))
    return result.scalars().all()


async def count_payment_gateway(db: AsyncSession) -> int:
    result = await db.execute(select(func.count()).select_from(PaymentGateway))
    return result.scalar_one()


async def create_payment_gateway(payload: dict, db: AsyncSession) -> PaymentGateway:
    _payment_gateway = await db.scalar(select(PaymentGateway).filter(func.lower(PaymentGateway.name) == payload['name'].lower()))
    if _payment_gateway:
        raise ConflictException('Payment Gateway with name {} already exists'.format(
            _payment_gateway.name), str(_payment_gateway.id))

    logger.debug('Creating Payment Gateway with payload: %s', payload)
    payment_gateway = PaymentGateway(**payload)
    db.add(payment_gateway)
    await db.commit()

    logger.info(f'Payment Gateway created {payment_gateway}')
    return payment_gateway


async def update_payment_gateway(id: UUID, payload: dict, db: AsyncSession) -> PaymentGateway:
    payment_gateway = await get_payment_gateway_by_id(id, db)

    logger.debug('Updating Payment Gateway with payload: %s', payload)
    [setattr(payment_gateway, key, value)
     for key, value in payload.items()]
    await db.commit()

    logger.info(f'Payment Gateway updated {payment_gateway}')
    return payment_gateway


async def delete_payment_gateway(id: UUID, db: AsyncSession) -> None:
    payment_gateway = await db.get(PaymentGateway, id)
    if not payment_gateway:
        raise NotFoundException('Payment Gateway not found')
    await db.delete(payment_gateway)
    await db.commit()

    logger.info(f'Payment Gateway deleted {payment_gateway}')
