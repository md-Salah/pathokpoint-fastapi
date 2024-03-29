import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from httpx import AsyncClient, ASGITransport
from typing import AsyncGenerator
from fastapi import status
from unittest.mock import patch

from app.main import app
from app.config.database import get_db, Base
from app.config.settings import settings
from app.constant import Country


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

    await engine.dispose()


@pytest_asyncio.fixture(name="client")
async def client_fixture(session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:

    async with ASGITransport(app=app) as transport:  # type: ignore
        async with AsyncClient(transport=transport, base_url=settings.BASE_URL) as client:
            app.dependency_overrides[get_db] = lambda: session
            yield client
            app.dependency_overrides.clear()


# Other fixtures
@pytest_asyncio.fixture(name="image_in_db")
@patch("app.controller.image.upload_file_to_cloudinary")
async def create_image(upload_file, client: AsyncClient):
    upload_file.return_value = 'https://res.cloudinary.com/dummy/image/upload/v1629780000/test.jpg'
    
    with open("dummy/test.jpg", "rb") as f:
        response = await client.post("/image",
                                     files={"file": ("image.jpg", f, "image/jpeg")}, data={'alt': 'test-image'})
    assert response.status_code == status.HTTP_201_CREATED
    upload_file.assert_called_once()
    return response.json()


@pytest_asyncio.fixture(name="author_in_db")
async def create_author(client: AsyncClient, image_in_db: dict):
    response = await client.post("/author", json={
        "birth_date": "1948-11-13",
        "book_published": 200,
        "city": "dhaka",
        "country": "BD",
        "death_date": "2012-07-19",
        "description": "বাংলাদেশের প্রখ্যাত লেখক",
        "is_popular": True,
        "name": "হুমায়ূন আহমেদ",
        "slug": "humayun-ahmed",
        "image": image_in_db["id"],
        "banner": image_in_db['id'],
    })
    assert response.status_code == status.HTTP_201_CREATED
    return response.json()


@pytest_asyncio.fixture(name="publisher_in_db")
async def create_publisher(client: AsyncClient):
    response = await client.post("/publisher", json={
        "name": "Rupa Publications",
        "slug": "rupa-publications",
        "is_popular": True,
        "country": Country.BD.value,
    })
    assert response.status_code == status.HTTP_201_CREATED
    return response.json()


@pytest_asyncio.fixture(name="category_in_db")
async def create_category(client: AsyncClient):
    response = await client.post("/category", json={
        "name": "Fiction",
        "slug": "fiction",
        'is_popular': True,
    })
    assert response.status_code == status.HTTP_201_CREATED
    return response.json()


@pytest_asyncio.fixture(name="user_in_db")
async def create_user(client: AsyncClient):
    response = await client.post("/signup", json={
        "email": "testuser@gmail.com",
        "password": "testPassword2235#",
        "phone_number": "+8801311701123",
        "first_name": "test",
        "last_name": "user",
        "username": "testUser1"
    })
    assert response.status_code == status.HTTP_201_CREATED
    return response.json()


@pytest_asyncio.fixture(name="admin_in_db")
async def create_admin(client: AsyncClient):
    response = await client.post("/user", json={
        "email": "testadmin@gmail.com",
        "password": "testPassword2235#",
        "phone_number": "+8801311701123",
        "first_name": "test",
        "last_name": "user",
        "username": "testadmin",
        "role": "admin"
    })
    assert response.status_code == status.HTTP_201_CREATED
    return response.json()

