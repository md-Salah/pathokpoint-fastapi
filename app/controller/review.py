from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import joinedload, selectinload
from typing import Sequence
from uuid import UUID
import logging

from app.filter_schema.review import ReviewFilter
from app.models.review import Review, review_image_link
from app.models.book import Book
from app.models.order import Order
from app.controller.exception import NotFoundException, ForbiddenException
from app.controller.user import get_user_by_id
from app.controller.image import handle_multiple_image_attachment
from app.controller.auth import Role

logger = logging.getLogger(__name__)


async def get_review_by_id(id: UUID, db: AsyncSession) -> Review:
    stmt = select(Review).options(selectinload(Review.user),
                                  selectinload(Review.images)).filter(Review.id == id)

    review = await db.scalar(stmt)
    if not review:
        raise NotFoundException('Review not found', str(id))
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
        book = await db.scalar(select(Book).filter(Book.id == book_id))
        if not book:
            raise NotFoundException('Book not found', str(book_id))
        payload['book'] = book
    elif order_id := payload.pop('order_id', None):
        order = await db.scalar(select(Order).filter(Order.id == order_id))
        if not order:
            raise NotFoundException('Order not found', str(order_id))
        elif order.customer_id != payload['user_id']:
            raise ForbiddenException(
                'You are not allowed to review this order', str(order_id))
        payload['order'] = order

    if 'images' in payload:
        # payload['images'] = await attach_images(payload['images'], [], db)
        payload['images'] = await handle_multiple_image_attachment(payload['images'], [], db, review_image_link)

    payload['average_rating'] = (payload['product_rating'] + payload['delivery_rating'] +
                                 payload['time_rating'] + payload['website_rating']) / 4

    logger.debug(payload)
    review = Review(**payload)
    db.add(review)
    await db.commit()
    logger.info(f'Review created {review} by {review.user}')
    return review


async def update_review(id: UUID, user_id: UUID, payload: dict, db: AsyncSession) -> Review:
    review = await get_review_by_id(id, db)
    if review.user_id != user_id:
        raise ForbiddenException('You are not allowed to update this review.')

    if 'images' in payload:
        previous_ids = [image.id for image in review.images]
        payload['images'] = await handle_multiple_image_attachment(payload['images'], previous_ids, db, review_image_link)

    logger.debug(payload)
    [setattr(review, key, value)
     for key, value in payload.items()]

    review.average_rating = (review.product_rating + review.delivery_rating +
                             review.time_rating + review.website_rating) / 4
    review.is_approved = False

    await db.commit()
    logger.info(f'Review updated {review}')
    return review


async def approve_review(id: UUID, db: AsyncSession) -> Review:
    review = await get_review_by_id(id, db)
    review.is_approved = True
    await db.commit()
    logger.info(f'Review approved {review}')
    return review


async def delete_review(id: UUID, user_id: UUID, user_role: str, db: AsyncSession) -> None:
    review = await db.get(Review, id)
    if not review:
        raise NotFoundException('Review not found', str(id))
    
    if user_id != review.user_id and user_role != Role.admin.value:
        raise ForbiddenException('You are not allowed to delete this review.')
    
    image_ids = [image.id for image in await review.awaitable_attrs.images]
    await handle_multiple_image_attachment([], image_ids, db, review_image_link)
    await db.delete(review)
    await db.commit()

    logger.info(f'Review deleted {review}')
