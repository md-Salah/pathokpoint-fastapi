from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import joinedload
from typing import Sequence
from uuid import UUID

from app.models.coupon import Coupon
from app.models import Book, Publisher, Author, Category, Tag, User

query = select(Coupon).options(
    joinedload(Coupon.include_books),
    joinedload(Coupon.include_authors),
    joinedload(Coupon.include_categories),
    joinedload(Coupon.include_publishers),
    joinedload(Coupon.include_tags),
    
    joinedload(Coupon.exclude_books),
    joinedload(Coupon.exclude_authors),
    joinedload(Coupon.exclude_categories),
    joinedload(Coupon.exclude_publishers),
    joinedload(Coupon.exclude_tags),
    
    joinedload(Coupon.allowed_users),
)

async def get_coupon_by_id(id: UUID, db: AsyncSession) -> Coupon:
    coupon = await db.scalar(query.where(Coupon.id == id))
    if not coupon:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Coupon with id ({id}) not found')
    return coupon


async def get_all_coupons(page: int, per_page: int, db: AsyncSession) -> Sequence[Coupon]:
    offset = (page - 1) * per_page
    result = await db.execute(query.offset(offset).limit(per_page))
    return result.scalars().unique().all()


async def create_coupon(payload: dict, db: AsyncSession) -> Coupon:
    if await db.scalar(select(Coupon).where(Coupon.code == payload['code'])):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Coupon with code ({}) already exists'.format(payload['code']))
    
    payload = await build_relationships(payload, db)    
    coupon = Coupon(**payload)
    db.add(coupon)
    await db.commit()
    return coupon


async def update_coupon(id: UUID, payload: dict, db: AsyncSession) -> Coupon:
    coupon = await db.scalar(query.where(Coupon.id == id))
    if not coupon:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Coupon with id ({id}) not found')
    
    payload = await build_relationships(payload, db)    
    [setattr(coupon, key, value)
     for key, value in payload.items()]
    await db.commit()
    return coupon


async def delete_coupon(id: UUID, db: AsyncSession) -> None:
    coupon = await get_coupon_by_id(id, db)
    await db.delete(coupon)
    await db.commit()


async def count_coupon(db: AsyncSession) -> int:
    result = await db.execute(select(func.count()).select_from(Coupon))
    return result.scalar_one()


async def build_relationships(payload: dict, db: AsyncSession) -> dict:
    if payload.get('include_books'):
        payload['include_books'] = [await db.get(Book, book_id) for book_id in payload['include_books']]
    if payload.get('include_authors'):
        payload['include_authors'] = [await db.get(Author, author_id) for author_id in payload['include_authors']]
    if payload.get('include_categories'):
        payload['include_categories'] = [await db.get(Category, category_id) for category_id in payload['include_categories']]
    if payload.get('include_publishers'):
        payload['include_publishers'] = [await db.get(Publisher, publisher_id) for publisher_id in payload['include_publishers']]
    if payload.get('include_tags'):
        payload['include_tags'] = [await db.get(Tag, tag_id) for tag_id in payload['include_tags']]
    
    if payload.get('exclude_books'):
        payload['exclude_books'] = [await db.get(Book, book_id) for book_id in payload['exclude_books']]
    if payload.get('exclude_authors'):
        payload['exclude_authors'] = [await db.get(Author, author_id) for author_id in payload['exclude_authors']]
    if payload.get('exclude_categories'):
        payload['exclude_categories'] = [await db.get(Category, category_id) for category_id in payload['exclude_categories']]
    if payload.get('exclude_publishers'):
        payload['exclude_publishers'] = [await db.get(Publisher, publisher_id) for publisher_id in payload['exclude_publishers']]
    if payload.get('exclude_tags'):
        payload['exclude_tags'] = [await db.get(Tag, tag_id) for tag_id in payload['exclude_tags']]
        
    if payload.get('allowed_users'):
        payload['allowed_users'] = [await db.get(User, user_id) for user_id in payload['allowed_users']]

    return payload
