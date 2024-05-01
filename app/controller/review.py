from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete
from sqlalchemy.orm import joinedload, selectinload
from typing import Sequence
from uuid import UUID
import logging

from app.filter_schema.review import ReviewFilter
from app.models.review import Review, review_image_link
from app.models.image import Image
from app.models.book import Book
from app.models.order import Order
from app.controller.exception import not_found_exception, forbidden_exception
from app.controller.user import get_user_by_id
import app.controller.image as image_service

logger = logging.getLogger(__name__)


async def get_review_by_id(id: UUID, db: AsyncSession) -> Review:
    stmt = select(Review).options(selectinload(Review.user),
                                  selectinload(Review.images)).filter(Review.id == id)

    review = await db.scalar(stmt)
    if not review:
        raise not_found_exception(str(id), 'Review not found')
    return review


async def get_all_reviews(page: int, per_page: int, filter: ReviewFilter, db: AsyncSession) -> Sequence[Review]:
    offset = (page - 1) * per_page
    stmt = select(Review).options(joinedload(
        Review.user), joinedload(Review.images))
    stmt = filter.filter(stmt)
    stmt = stmt.offset(offset).limit(per_page)

    result = await db.execute(stmt)
    return result.scalars().unique().all()


async def count_review(filter: ReviewFilter, db: AsyncSession) -> int:
    stmt = select(func.count()).select_from(Review)
    stmt = filter.filter(stmt)

    result = await db.execute(stmt)
    return result.scalar_one()


async def create_review(payload: dict, db: AsyncSession) -> Review:
    payload['user'] = await get_user_by_id(payload['user_id'], db)

    # Associate review with book or order
    if book_id := payload.pop('book_id', None):
        stmt = select(Book).filter(Book.id == book_id)

        payload['book'] = await db.scalar(stmt)
    elif order_id := payload.pop('order_id', None):
        stmt = select(Order).filter(Order.id == order_id)

        order = await db.scalar(stmt)
        if not order:
            raise not_found_exception(str(order_id), 'Order not found')
        elif order.customer_id != payload['user_id']:
            raise forbidden_exception(
                str(order_id), 'You are not allowed to review this order')
        payload['order'] = order

    if payload['images']:
        stmt = select(Image).filter(Image.id.in_(payload['images']))

        payload['images'] = (await db.scalars(stmt)).all()

    payload['average_rating'] = (payload['product_rating'] + payload['delivery_rating'] +
                                 payload['time_rating'] + payload['website_rating']) / 4

    logger.debug(payload)
    review = Review(**payload)
    db.add(review)
    await db.commit()
    return review


async def update_review(id: UUID, payload: dict, db: AsyncSession) -> Review:
    review = await get_review_by_id(id, db)

    if 'images' in payload:
        logger.debug('updating review images')
        if image_ids := payload.pop('images'):
            existing_ids = [image.id for image in review.images]

            stmt = select(Image).filter(Image.id.in_(
                [id for id in image_ids if id not in existing_ids]))
            review.images.extend((await db.scalars(stmt)).all())

            remove_list = [id for id in existing_ids if id not in image_ids]
            if remove_list:
                await image_service.delete_image_bulk(remove_list, db)
        else:
            exitsting_ids = [image.id for image in review.images]
            if exitsting_ids:
                await image_service.delete_image_bulk(exitsting_ids, db)
            review.images = []

    logger.debug(payload)
    [setattr(review, key, value)
     for key, value in payload.items()]

    # Recalculate average rating
    review.average_rating = (review.product_rating + review.delivery_rating +
                             review.time_rating + review.website_rating) / 4
    review.is_approved = False

    await db.commit()
    return review


async def approve_review(id: UUID, db: AsyncSession) -> Review:
    review = await get_review_by_id(id, db)
    review.is_approved = True
    await db.commit()
    return review


async def delete_review(id: UUID, db: AsyncSession) -> None:
    image_ids = (await db.scalars(select(review_image_link.c.image_id).where(review_image_link.c.review_id == id))).all()
    if image_ids:
        await image_service.delete_image_bulk(image_ids, db)
    await db.execute(delete(Review).where(Review.id == id))
    await db.commit()
