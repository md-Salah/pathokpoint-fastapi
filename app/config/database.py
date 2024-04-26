from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker, AsyncAttrs
from sqlalchemy.orm import DeclarativeBase

from app.config.settings import settings

class Base(AsyncAttrs, DeclarativeBase):
    pass

engine = create_async_engine(settings.DATABASE_URL, echo=not settings.PRODUCTION, future=True)
session_factory = async_sessionmaker(engine, autoflush=False, expire_on_commit=False)

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def drop_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with session_factory() as session:
        yield session



        
        