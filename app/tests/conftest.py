import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from httpx import AsyncClient, ASGITransport
from typing import AsyncGenerator
from fastapi import status
from unittest.mock import patch

import uuid
from app.main import app
from app.config.database import get_db, Base
from app.config.settings import settings
from app.constant import Country
from app.controller.auth import create_jwt_token
from app.constant.role import Role


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


# In DB fixtures
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
async def create_author(client: AsyncClient, admin_auth_headers: dict):
    response = await client.post("/author", json={
        "birth_date": "1948-11-13",
        "book_published": 200,
        "city": "dhaka",
        "country": "BD",
        "death_date": "2012-07-19",
        "description": "বাংলাদেশের প্রখ্যাত লেখক",
        "is_popular": True,
        "name": "হুমায়ূন আহমেদ",
        "slug": "humayun-ahmed"
    }, headers=admin_auth_headers)
    assert response.status_code == status.HTTP_201_CREATED
    return response.json()


@pytest_asyncio.fixture(name="publisher_in_db")
async def create_publisher(client: AsyncClient, admin_auth_headers: dict):
    response = await client.post("/publisher", json={
        "name": "Rupa Publications",
        "slug": "rupa-publications",
        "is_popular": True,
        "country": Country.BD.value,
    }, headers=admin_auth_headers)
    assert response.status_code == status.HTTP_201_CREATED
    return response.json()


@pytest_asyncio.fixture(name="category_in_db")
async def create_category(client: AsyncClient, admin_auth_headers: dict):
    response = await client.post("/category", json={
        "name": "Fiction",
        "slug": "fiction",
        'is_popular': True,
    }, headers=admin_auth_headers)
    assert response.status_code == status.HTTP_201_CREATED
    return response.json()


@pytest_asyncio.fixture(name="book_in_db")
async def create_book(client: AsyncClient, admin_auth_headers: dict):
    response = await client.post("/book", json={
        "sku": "99-5432",
        "name": "The Alchemist",
        "slug": "the-alchemist",
        "regular_price": 700,
        "sale_price": 250,
        "manage_stock": True,
        "quantity": 10,
        "is_used": True,
        "condition": "old-like-new",
        "is_popular": True,
    }, headers=admin_auth_headers)
    assert response.status_code == status.HTTP_201_CREATED
    return response.json()


@pytest_asyncio.fixture(name="user_in_db")
async def create_user_by_admin(client: AsyncClient, admin_auth_headers: dict):
    response = await client.post("/user", json={
        "email": "testuser@gmail.com",
        "password": "testPassword2235#",
        "phone_number": "+8801311701123",
        "first_name": "test",
        "last_name": "user",
        "role": "customer"
    }, headers=admin_auth_headers)
    assert response.status_code == status.HTTP_201_CREATED
    user = response.json()
    return {
        'user': user,
        'token': {
            'access_token': create_jwt_token(user['id'], Role.customer, 'access'),
        }
    }


@pytest_asyncio.fixture(name="admin_in_db")
async def create_admin_by_admin(client: AsyncClient, admin_auth_headers: dict):
    response = await client.post("/user", json={
        "email": "testadmin@gmail.com",
        "password": "testPassword2235#",
        "phone_number": "+8801478639075",
        "first_name": "test",
        "last_name": "user",
        "role": "admin"
    }, headers=admin_auth_headers)
    assert response.status_code == status.HTTP_201_CREATED
    return response.json()


@pytest_asyncio.fixture(name="courier_in_db")
async def create_courier(client: AsyncClient):
    response = await client.post("/courier", json={
        "method_name": "Delivery Tiger - Inside Dhaka",
        "company_name": "Delivery Tiger",
        "base_charge": 60.0,
        "weight_charge_per_kg": 20.0,
        "allow_cash_on_delivery": True,
        "include_country": ["BD"],
        "include_city": ["dhaka"],
        "exclude_city": [],
    })
    assert response.status_code == status.HTTP_201_CREATED
    return response.json()


@pytest_asyncio.fixture(name="address_in_db")
async def create_address(client: AsyncClient, user_in_db: dict):
    response = await client.post(f"/address/{user_in_db['user']['id']}", json={
        "phone_number": "+8801710002000",
        "alternative_phone_number": "+8801710000001",
        "address": "House 1, Road 1, Block A, Dhaka",
        "thana": "dhanmondi",
        "city": "dhaka",
        "country": "BD",
    })
    assert response.status_code == status.HTTP_201_CREATED
    return response.json()


@pytest_asyncio.fixture(name="coupon_in_db")
async def create_coupon(client: AsyncClient):
    response = await client.post("/coupon", json={
        "code": "NewYear",
        "short_description": "New year coupon",
        "expiry_date": "2024-12-31T00:00:00",
        "discount_type": "percentage",
        "discount_old": 15,
        "discount_new": 0,
        "min_spend_old": 499,
        "min_spend_new": 0,
    })
    assert response.status_code == status.HTTP_201_CREATED
    return response.json()


@pytest_asyncio.fixture(name="order_in_db")
async def create_order(client: AsyncClient, book_in_db: dict):
    response = await client.post("/order/admin/new", json={
        "order_items": [
            {
                "book_id": book_in_db["id"],
                "quantity": 1,
            }
        ]
    })
    assert response.status_code == status.HTTP_201_CREATED
    return response.json()


@pytest_asyncio.fixture(name="payment_gateway_in_db")
async def create_payment_gateway(client: AsyncClient):
    response = await client.post("/payment_gateway", json={
        "name": "Bkash",
        "description": "Bkash Payment Gateway",
        "is_enabled": True
    })
    assert response.status_code == status.HTTP_201_CREATED
    return response.json()


@pytest_asyncio.fixture(name="review_in_db")
async def create_review(client: AsyncClient, image_in_db: dict, book_in_db: dict, user_in_db: dict):
    response = await client.post("/review/new", json={
        "product_rating": 5,
        "time_rating": 5,
        "delivery_rating": 5,
        "website_rating": 5,
        "comment": "Great book I have ever read!",
        "book_id": book_in_db["id"],
        "images": [image_in_db["id"]],
    }, headers={"Authorization": f"Bearer {user_in_db["token"]['access_token']}"})
    assert response.status_code == status.HTTP_201_CREATED
    return {**response.json(), 'access_token': user_in_db["token"]['access_token']}


@pytest_asyncio.fixture(name="customer_access_token")
async def get_access_token():
    return create_jwt_token(uuid.uuid4(), Role.customer, 'access')


@pytest_asyncio.fixture(name="admin_access_token")
async def get_admin_access_token():
    return create_jwt_token(uuid.uuid4(), Role.admin, 'access')


@pytest_asyncio.fixture(name='admin_auth_headers')
async def get_admin_auth_headers_with_bearer_token(admin_access_token: str):
    return {
        'Authorization': f'Bearer {admin_access_token}'
    }


@pytest_asyncio.fixture(name='customer_auth_headers')
async def get_auth_headers_with_bearer_token(customer_access_token: str):
    return {
        'Authorization': f'Bearer {customer_access_token}'
    }
