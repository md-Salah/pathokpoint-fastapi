import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from httpx import AsyncClient, ASGITransport
from typing import AsyncGenerator


from app.main import app
from app.config.database import get_db, Base
from app.config.settings import settings


@pytest_asyncio.fixture(name="session")
async def session_fixture():
    engine = create_async_engine(settings.TEST_DATABASE_URL)
    session_factory = async_sessionmaker(
        engine, autoflush=False, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with session_factory() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(name="client")
async def client_fixture(session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:

    async with ASGITransport(app=app) as transport:  # type: ignore
        async with AsyncClient(transport=transport, base_url=settings.BASE_URL) as client:
            app.dependency_overrides[get_db] = lambda: session
            yield client
            app.dependency_overrides.clear()
