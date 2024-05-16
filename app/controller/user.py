import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete
from uuid import UUID
from typing import Sequence
from pydantic import SecretStr
import re
import random
import string

from app.filter_schema.user import UserFilter
from app.models.user import User
import app.controller.auth as auth_service
from app.controller.exception import NotFoundException, BadRequestException

logger = logging.getLogger(__name__)


async def is_user_exist(email: str, db: AsyncSession) -> bool:
    user = await db.scalar(select(User).where(User.email == email))
    return True if user else False

async def is_super_admin_exist(db: AsyncSession) -> bool:
    user = await db.scalar(select(User).where(User.role == 'super_admin'))
    return True if user else False

async def get_user_by_id(id: UUID, db: AsyncSession) -> User:
    user = await db.get(User, id)
    if not user:
        raise NotFoundException('User not found', str(id))
    return user


async def get_user_by_email(email: str, db: AsyncSession) -> User:
    user = await db.scalar(select(User).where(User.email == email))
    if not user:
        raise NotFoundException('User not found')
    return user


async def get_all_users(filter: UserFilter, page: int, per_page: int, db: AsyncSession) -> Sequence[User]:
    offset = (page - 1) * per_page
    query = select(User).outerjoin(User.addresses)
    query = filter.filter(query)
    query = query.offset(offset).limit(per_page)
    result = await db.execute(query)
    return result.scalars().all()


async def count_user(filter: UserFilter, db: AsyncSession) -> int:
    query = select(func.count(User.id)).outerjoin(User.addresses)
    query = filter.filter(query)
    result = await db.execute(query)
    return result.scalar_one()


async def create_user(payload: dict, db: AsyncSession) -> User:
    if await db.scalar(select(User).where(User.email == payload['email'])):
        raise BadRequestException(
            'User already exists with email {}'.format(payload['email']))

    payload['username'] = await generate_unique_username(payload['first_name'], payload['last_name'], db)

    if isinstance(payload['password'], SecretStr):
        payload['password'] = auth_service.get_hashed_password(
            payload['password'].get_secret_value())

    user = User(**payload)
    db.add(user)
    await db.commit()

    logger.info(f'User created successfully, {user}')
    return user


async def update_user(id: UUID, payload: dict, db: AsyncSession) -> User:
    user = await get_user_by_id(id, db)

    if 'password' in payload and isinstance(payload['password'], SecretStr):
        payload['password'] = auth_service.get_hashed_password(
            payload['password'].get_secret_value())

    print(payload.items())
    [setattr(user, key, value) for key, value in payload.items()]
    await db.commit()
    return user


async def delete_user(id: UUID, db: AsyncSession) -> None:
    await db.execute(delete(User).where(User.id == id))
    await db.commit()
    logger.info(f'User with id ({id}) deleted successfully')


async def generate_unique_username(f_name: str, l_name: str, db: AsyncSession) -> str:
    username_base = f"{f_name}-{l_name}"
    username_base = re.sub(r'[^a-zA-Z0-9_.-]', '-', username_base)

    if len(username_base) < 5:
        ln = 5 - len(username_base)
        username_base += ''.join(random.choices(string.digits, k=ln))
    elif len(username_base) > 20:
        username_base = username_base[:20]

    results = await db.execute(select(User).where(User.username.like(username_base + '%')))
    ln = len(results.scalars().all())
    return f"{username_base}-{ln}" if ln else username_base
