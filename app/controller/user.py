from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, update
from uuid import UUID
from typing import Sequence

from app.models.user import User
import app.controller.auth as auth_service
from app.constant import Role


async def is_user_exist(email: str, db: AsyncSession) -> bool:
    user = await db.scalar(select(User).where(User.email == email))
    return True if user else False


async def get_user_by_id(id: UUID, db: AsyncSession) -> User:
    user = await db.get(User, id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'User with id ({id}) not found')
    return user


async def get_user_by_email(email: str, db: AsyncSession) -> User:
    user = await db.scalar(select(User).where(User.email == email))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'User with email ({email}) not found')
    return user


async def get_all_users(q: str | None, role: Role | None, page: int, per_page: int, db: AsyncSession) -> Sequence[User]:
    offset = (page - 1) * per_page
    query = select(User)
    if role:
        query = query.where(User.role == role)
    if q:
        query = query.where(or_(User.email.ilike(
            f'%{q}%'), User.phone_number.like(f'%{q}%')))
    query = query.offset(offset).limit(per_page)
    result = await db.execute(query)
    return result.scalars().all()


async def create_user(payload: dict, db: AsyncSession) -> User:
    if await db.scalar(select(User).where(User.email == payload['email'])):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='User with email ({}) already exists'.format(payload['email']))

    payload['username'] = await generate_unique_username(payload, db)
    payload['password'] = auth_service.get_hashed_password(
        payload['password'].get_secret_value())

    user = User(**payload)
    db.add(user)
    await db.commit()

    return user


async def update_user(id: UUID, payload: dict, db: AsyncSession) -> User:
    user = await get_user_by_id(id, db)
    if payload.get('email') and payload.get('is_verified') is None:
        payload['is_verified'] = False
    if payload.get('username'):
        payload['username'] = await generate_unique_username(payload, db)
    if payload.get('password'):
        payload['password'] = auth_service.get_hashed_password(
            payload['password'].get_secret_value())

    [setattr(user, key, value) for key, value in payload.items()]
    await db.commit()
    return user

async def delete_user(id: UUID, db: AsyncSession) -> None:
    user = await get_user_by_id(id, db)
    await db.delete(user)
    await db.commit()


async def generate_unique_username(payload, db: AsyncSession) -> str:
    if payload['username']:
        username_base = payload['username']
    elif payload['first_name'] and payload['last_name']:
        username_base = payload['first_name'] + payload['last_name']
    else:
        username_base = payload['email'].split('@')[0]
    username_base = username_base.replace(' ', '-')
    if len(username_base) < 5:
        username_base += 'user'
    elif len(username_base) > 20:
        username_base = username_base[:20]

    results = await db.execute(select(User).where(User.username.like(username_base + '%')))
    ln = len(results.scalars().all())
    return f"{username_base}-{ln}" if ln else username_base


async def count_user(q: str | None, role: Role | None, db: AsyncSession) -> int:
    query = select(func.count(User.id))
    if role:
        query = query.where(User.role == role)
    if q:
        query = query.where(or_(User.email.ilike(
            f'%{q}%'), User.phone_number.like(f'%{q}%')))
    result = await db.execute(query)
    return result.scalar_one()
