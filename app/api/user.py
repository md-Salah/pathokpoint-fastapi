from fastapi import APIRouter, Depends, status, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.config.database import get_db
import app.controller.user as user_service
import app.pydantic_schema.user as user_schema
from app.constant import Role

router = APIRouter(prefix='/user')


@router.get('/id/{id}', response_model=user_schema.UserOut)
async def get_user_by_id(id: UUID, db: AsyncSession = Depends(get_db)):
    user = await user_service.get_user_by_id(id, db)
    return user_schema.UserOut.model_validate(user)


@router.get('/all', response_model=list[user_schema.UserOut])
async def get_all_users(*, q: str | None = Query(None, min_length=3, max_length=50, description='Search by email or phone number'),
                        role: Role | None = Query(
                            None, description="Filter by role"),
                        page: int = Query(1, ge=1),
                        per_page: int = Query(10, ge=1, le=100),
                        db: AsyncSession = Depends(get_db),  response: Response):
    users = await user_service.get_all_users(q, role, page, per_page, db)
    total_result = await user_service.count_user(q, role, db)

    response.headers['X-Total-Count'] = str(total_result)
    response.headers['X-Total-Pages'] = str(-(-total_result // per_page))
    response.headers['X-Current-Page'] = str(page)
    response.headers['X-Per-Page'] = str(per_page)

    return [user_schema.UserOut.model_validate(user) for user in users]


@router.post('', response_model=user_schema.UserOut, status_code=status.HTTP_201_CREATED)
async def create_user_by_admin(payload: user_schema.CreateUserByAdmin, db: AsyncSession = Depends(get_db)):
    user = await user_service.create_user(payload.model_dump(), db)
    return user_schema.UserOut.model_validate(user)


@router.patch('/profile/{id}', response_model=user_schema.UserOut)
async def update_user(id: UUID, payload: user_schema.UpdateUser, db: AsyncSession = Depends(get_db)):
    user = await user_service.update_user(id, payload.model_dump(exclude_unset=True), db)
    return user_schema.UserOut.model_validate(user)


@router.patch('/{user_id}', response_model=user_schema.UserOut)
async def update_user_by_admin(user_id: UUID, payload: user_schema.UpdateUserByAdmin, db: AsyncSession = Depends(get_db)):
    user = await user_service.update_user(user_id, payload.model_dump(exclude_unset=True), db)
    return user_schema.UserOut.model_validate(user)


@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(id: UUID, db: AsyncSession = Depends(get_db)):
    await user_service.delete_user(id, db)
