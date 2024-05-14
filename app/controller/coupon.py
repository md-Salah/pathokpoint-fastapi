from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import Sequence
from uuid import UUID
import logging

from app.models.coupon import Coupon
from app.models import Book, Publisher, Author, Category, Tag, User
from app.controller.exception import NotFoundException, ConflictException
from app.filter_schema.coupon import CouponFilter

logger = logging.getLogger(__name__)

query = select(Coupon).options(
    selectinload(Coupon.include_books),
    selectinload(Coupon.include_authors),
    selectinload(Coupon.include_categories),
    selectinload(Coupon.include_publishers),
    selectinload(Coupon.include_tags),

    selectinload(Coupon.exclude_books),
    selectinload(Coupon.exclude_authors),
    selectinload(Coupon.exclude_categories),
    selectinload(Coupon.exclude_publishers),
    selectinload(Coupon.exclude_tags),

    selectinload(Coupon.allowed_users),
)


async def get_coupon_by_id(id: UUID, db: AsyncSession) -> Coupon:
    coupon = await db.scalar(query.where(Coupon.id == id))
    if not coupon:
        raise NotFoundException('Coupon not found')
    return coupon


async def get_all_coupons(filter: CouponFilter, page: int, per_page: int, db: AsyncSession) -> Sequence[Coupon]:
    offset = (page - 1) * per_page
    stmt = select(Coupon).offset(offset).limit(per_page)
    stmt = filter.filter(stmt)
    stmt = filter.sort(stmt)
    result = await db.execute(stmt)
    return result.scalars().unique().all()


async def count_coupon(filter: CouponFilter, db: AsyncSession) -> int:
    stmt = select(func.count()).select_from(Coupon)
    stmt = filter.filter(stmt)
    result = await db.execute(stmt)
    return result.scalar_one()


async def create_coupon(payload: dict, db: AsyncSession) -> Coupon:
    _coupon = await db.scalar(select(Coupon).where(Coupon.code.ilike(payload['code'])))
    if _coupon:
        raise ConflictException('Coupon code already exists', str(_coupon.id))

    payload = await build_relationships(payload, db)
    logger.debug(f'Creating coupon with payload: {payload}')
    coupon = Coupon(**payload)
    db.add(coupon)
    await db.commit()
    logger.info(f'Coupon created successfully {coupon}')
    return coupon


async def update_coupon(id: UUID, payload: dict, db: AsyncSession) -> Coupon:
    coupon = await db.scalar(query.where(Coupon.id == id))
    if not coupon:
        raise NotFoundException('Coupon not found')

    payload = await build_relationships(payload, db)
    logger.debug(f'Updating coupon {coupon} with payload: {payload}')
    [setattr(coupon, key, value)
     for key, value in payload.items()]
    await db.commit()
    logger.info(f'Coupon updated successfully {coupon}')
    return coupon


async def delete_coupon(id: UUID, db: AsyncSession) -> None:
    coupon = await db.get(Coupon, id)
    if not coupon:
        raise NotFoundException('Coupon not found')
    await db.delete(coupon)
    await db.commit()

    logger.info(f'Coupon deleted successfully {coupon}')


async def build_relationships(payload: dict, db: AsyncSession) -> dict:
    if payload.get('include_books'):
        payload['include_books'] = list((await db.scalars(select(Book).where(Book.id.in_(payload['include_books'])))).all())

    if payload.get('exclude_books'):
        payload['exclude_books'] = list((await db.scalars(select(Book).where(Book.id.in_(payload['exclude_books'])))).all())

    if payload.get('include_authors'):
        payload['include_authors'] = list((await db.scalars(select(Author).where(Author.id.in_(payload['include_authors'])))).all())

    if payload.get('exclude_authors'):
        payload['exclude_authors'] = list((await db.scalars(select(Author).where(Author.id.in_(payload['exclude_authors'])))).all())

    if payload.get('include_categories'):
        payload['include_categories'] = list((await db.scalars(select(Category).where(Category.id.in_(payload['include_categories'])))).all())

    if payload.get('exclude_categories'):
        payload['exclude_categories'] = list((await db.scalars(select(Category).where(Category.id.in_(payload['exclude_categories'])))).all())

    if payload.get('include_publishers'):
        payload['include_publishers'] = list((await db.scalars(select(Publisher).where(Publisher.id.in_(payload['include_publishers'])))).all())

    if payload.get('exclude_publishers'):
        payload['exclude_publishers'] = list((await db.scalars(select(Publisher).where(Publisher.id.in_(payload['exclude_publishers'])))).all())

    if payload.get('include_tags'):
        payload['include_tags'] = list((await db.scalars(select(Tag).where(Tag.id.in_(payload['include_tags'])))).all())

    if payload.get('exclude_tags'):
        payload['exclude_tags'] = list((await db.scalars(select(Tag).where(Tag.id.in_(payload['exclude_tags'])))).all())

    if payload.get('allowed_users'):
        payload['allowed_users'] = list((await db.scalars(select(User).where(User.id.in_(payload['allowed_users'])))).all())

    return payload

