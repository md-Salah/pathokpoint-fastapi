from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from uuid import UUID
from typing import Sequence

from app.models.user import User


async def is_user_exist(db: AsyncSession, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    result = await db.execute(statement)
    return result.scalars().first()


async def is_username_exist(db: AsyncSession, username: str) -> User | None:
    statement = select(User).where(User.username == username)
    result = await db.execute(statement)
    return result.scalars().first()


async def get_user_by_id(id: UUID, db: AsyncSession) -> User:
    user = await db.get(User, id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'User with id ({id}) not found')
    return user


async def get_all_users(page: int, per_page: int, db: AsyncSession) -> Sequence[User]:
    offset = (page - 1) * per_page
    result = await db.execute(select(User).offset(offset).limit(per_page))
    return result.scalars().all()


async def create_user(payload: dict, db: AsyncSession) -> User:
    payload['username'] = await generate_unique_username(payload, db)

    new_user = User(**payload)
    db.add(new_user)
    await db.commit()

    return new_user


async def update_user(id: UUID, payload: dict, db: AsyncSession) -> User:
    user = await get_user_by_id(id, db)
    [setattr(user, key, value) for key, value in payload.items()]
    await db.commit()
    return user


async def delete_user(id: UUID, db: AsyncSession) -> None:
    user = await get_user_by_id(id, db)
    await db.delete(user)
    await db.commit()


async def generate_unique_username(payload, db: AsyncSession) -> str:
    username_base = payload['username'] if payload.get('username') else payload['first_name'].lower() + \
        payload['last_name'].lower()
    username_base = username_base.replace(' ', '-')
    results = await db.execute(select(User).where(User.username.like(f'{username_base}%')))
    ln = len(results.scalars().all())
    return f"{username_base}-{ln}" if ln else username_base


async def count_user(db: AsyncSession) -> int:
    result = await db.execute(select(func.count()).select_from(User))
    return result.scalar_one()
