from fastapi import APIRouter, status, Query, Response
from uuid import UUID
from fastapi_filter import FilterDepends

from app.filter_schema.user import UserFilter
from app.config.database import Session
import app.controller.user as user_service
import app.pydantic_schema.user as user_schema
from app.controller.auth import CurrentUser, AdminAccessToken

router = APIRouter(prefix='/user')


@router.get('/me', response_model=user_schema.UserOut)
async def me(user: CurrentUser):
    return user


@router.get('/id/{id}', response_model=user_schema.UserOut)
async def get_user_by_id_admin(id: UUID, db: Session, _: AdminAccessToken):
    return await user_service.get_user_by_id(id, db)


@router.get('/all', response_model=list[user_schema.UserOut])
async def get_all_users_by_admin(*, filter: UserFilter = FilterDepends(UserFilter),
                                 page: int = Query(1, ge=1),
                                 per_page: int = Query(10, ge=1, le=100),
                                 db: Session,  response: Response, _: AdminAccessToken):
    users = await user_service.get_all_users(filter, page, per_page, db)
    total_result = await user_service.count_user(filter, db)

    response.headers['X-Total-Count'] = str(total_result)
    response.headers['X-Total-Pages'] = str(-(-total_result // per_page))
    response.headers['X-Current-Page'] = str(page)
    response.headers['X-Per-Page'] = str(per_page)

    return users


@router.post('', response_model=user_schema.UserOut, status_code=status.HTTP_201_CREATED)
async def create_user_by_admin(payload: user_schema.CreateUserByAdmin, db: Session, _: AdminAccessToken):
    return await user_service.create_user(payload.model_dump(), db)


@router.patch('/me', response_model=user_schema.UserOut)
async def update_me(payload: user_schema.UpdateMe, db: Session, user: CurrentUser):
    return await user_service.update_user(user.id, payload.model_dump(exclude_unset=True), db)


@router.patch('/id/{id}', response_model=user_schema.UserOut)
async def update_user_by_admin(id: UUID, _: AdminAccessToken, payload: user_schema.UpdateUserByAdmin, db: Session):
    return await user_service.update_user(id, payload.model_dump(exclude_unset=True), db)

# upload profile picture


@router.delete('/me', status_code=status.HTTP_204_NO_CONTENT)
async def delete_me(user: CurrentUser, db: Session):
    await user_service.delete_user(user.id, db)


@router.delete('/id/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_by_admin(id: UUID, _: AdminAccessToken, db: Session):
    await user_service.delete_user(id, db)
