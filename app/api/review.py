from fastapi import APIRouter, status, Query, Response
from uuid import UUID
import logging
from fastapi_filter import FilterDepends

from app.filter_schema.review import ReviewFilter
from app.config.database import Session
from app.controller.auth import AccessToken, AdminAccessToken, Role
from app.controller.exception import ForbiddenException
import app.controller.review as review_service
import app.pydantic_schema.review as schema

logger = logging.getLogger(__name__)

router = APIRouter(prefix='/review')


@router.get('/id/{id}', response_model=schema.ReviewOut)
async def get_review_by_id(id: UUID, db: Session):
    return await review_service.get_review_by_id(id, db)


@router.get('/all', response_model=list[schema.ReviewOut])
async def get_all_reviews(*, page: int = Query(1, ge=1),
                          per_page: int = Query(10, ge=1, le=100),
                          filter: ReviewFilter = FilterDepends(ReviewFilter),
                          db: Session,  response: Response):
    reviews = await review_service.get_all_reviews(page, per_page, filter, db)
    total_reviews = await review_service.count_review(filter, db)

    response.headers['X-Total-Count'] = str(total_reviews)
    response.headers['X-Total-Pages'] = str(-(-total_reviews // per_page))
    response.headers['X-Current-Page'] = str(page)
    response.headers['X-Per-Page'] = str(per_page)

    return reviews


@router.post('/new', response_model=schema.ReviewOut, status_code=status.HTTP_201_CREATED)
async def create_review(payload: schema.CreateReview, token: AccessToken, db: Session):
    return await review_service.create_review({
        **payload.model_dump(),
        'user_id': token['id']
    }, db)


@router.patch('/{id}', response_model=schema.ReviewOut)
async def update_review(id: UUID, payload: schema.UpdateReview, token: AccessToken, db: Session):
    review = await review_service.get_review_by_id(id, db)
    if review.user_id == token['id']:
        return await review_service.update_review(id, payload.model_dump(exclude_unset=True), db)

    raise ForbiddenException('You are not allowed to update this review.')


@router.patch('/approve/{id}', response_model=schema.ReviewOut)
async def approve_review(id: UUID, _: AdminAccessToken, db: Session):
    return await review_service.approve_review(id, db)


@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(id: UUID, token: AccessToken, db: Session):

    if token['role'] == Role.admin.value:
        logger.info('Admin is deleting review')
        return await review_service.delete_review(id, db)
    else:
        review = await review_service.get_review_by_id(id, db)
        if review.user_id == token['id']:
            logger.info('User is deleting his review')
            return await review_service.delete_review(id, db)

    raise ForbiddenException(
        'You are not allowed to delete this review.', str(id))
