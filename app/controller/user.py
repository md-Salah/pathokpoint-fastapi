from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
import app.pydantic_schema.user as user_schema


async def is_user_exist(db: AsyncSession, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    result = await db.execute(statement)
    return result.scalars().first()

async def is_username_exist(db: AsyncSession, username: str) -> User | None:
    statement = select(User).where(User.username == username)
    result = await db.execute(statement)
    return result.scalars().first()

async def create_user(db: AsyncSession, user: user_schema.CreateUser) -> user_schema.ReadUser:
    user.username = await generate_unique_username(user, db)

    new_user = User(**user.model_dump())
    db.add(new_user)
    await db.commit() 
    
    return new_user


# Additional functions
async def generate_unique_username(payload, db: AsyncSession) -> str:
    username_base = payload.username if payload.username else payload.first_name.lower() + payload.last_name.lower()
    username_base = username_base.replace(' ', '-')
    results = await db.execute(select(User).where(User.username.like(f'{username_base}%')))
    return f"{username_base}-{len(results.scalars().all())}" if results else username_base