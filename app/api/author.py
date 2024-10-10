from uuid import UUID

from fastapi import APIRouter, Query, Response, status
from fastapi_filter import FilterDepends

import app.controller.author as author_service
import app.pydantic_schema.author as author_schema
from app.config.database import Session
from app.controller.auth import AccessToken, AdminAccessToken
from app.filter_schema.author import AuthorFilter

router = APIRouter(prefix='/author')


@router.get('/id/{id}', response_model=author_schema.AuthorOut)
async def get_author_by_id(id: UUID, db: Session):
    return await author_service.get_author_by_id(id, db)


@router.get('/slug/{slug}', response_model=author_schema.AuthorOut)
async def get_author_by_slug(slug: str, db: Session):
    return await author_service.get_author_by_slug(slug, db)


@router.get('/all', response_model=list[author_schema.AuthorOut])
async def get_all_authors(*,
                          filter: AuthorFilter = FilterDepends(
                              AuthorFilter),
                          page: int = Query(1, ge=1), per_page: int = Query(10, ge=1, le=100),
                          db: Session,
                          response: Response):
    authors = await author_service.get_all_authors(filter, page, per_page, db)

    total_result = await author_service.count_author(filter, db)
    response.headers['X-Total-Count'] = str(total_result)
    response.headers['X-Total-Pages'] = str(-(-total_result // per_page))
    response.headers['X-Current-Page'] = str(page)
    response.headers['X-Per-Page'] = str(per_page)

    return authors


@router.post('', response_model=author_schema.AuthorOut, status_code=status.HTTP_201_CREATED)
async def create_author(payload: author_schema.CreateAuthor, _: AdminAccessToken, db: Session):
    return await author_service.create_author(payload.model_dump(), db)


@router.patch('/{id}', response_model=author_schema.AuthorOut)
async def update_author(id: UUID, payload: author_schema.UpdateAuthor, _: AdminAccessToken, db: Session):
    return await author_service.update_author(id, payload.model_dump(exclude_unset=True), db)


@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_author(id: UUID, _: AdminAccessToken, db: Session):
    return await author_service.delete_author(id, db)


@router.post('/follow/{id}', response_model=author_schema.MsgSchema)
async def follow_author(id: UUID, token: AccessToken, db: Session) -> dict:
    return await author_service.follow_author(id, token['id'], db)


@router.post('/unfollow/{id}', response_model=author_schema.MsgSchema)
async def unfollow_author(id: UUID, token: AccessToken, db: Session) -> dict:
    return await author_service.unfollow_author(id, token['id'], db)


@router.get('/is-following/{id}', response_model=bool)
async def is_following(id: UUID, token: AccessToken, db: Session) -> bool:
    return await author_service.is_following_author(id, token['id'], db)


@router.get('/following', response_model=list[author_schema.AuthorOut])
async def get_following_authors(*, token: AccessToken,
                                page: int = Query(1, ge=1), per_page: int = Query(10, ge=1, le=100),
                                db: Session):
    return await author_service.get_following_authors(token['id'], page, per_page, db)
