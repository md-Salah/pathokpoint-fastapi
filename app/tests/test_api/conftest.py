from fastapi import status
from httpx import AsyncClient
import pytest_asyncio
from unittest.mock import patch, MagicMock
import uuid
import pytest
from typing import Any, Callable, Dict, Generator

from app.constant import Country
from app.controller.auth import create_jwt_token
from app.constant.role import Role


@pytest.fixture(name="mock_upload_file")
def mock_upload_file() -> Generator:
    with patch("app.controller.image.upload_file_to_cloudinary") as mock_upload_file:
        yield mock_upload_file


@pytest.fixture(name="mock_delete_file")
def mock_delete_file() -> Generator:
    with patch("app.models.image.delete_file_from_cloudinary_sync") as mock_delete_file:
        yield mock_delete_file


@pytest.fixture(name="send_invoice")
def send_invoice() -> Generator:
    with patch("app.api.order.email_service.send_invoice_email") as send_invoice:
        yield send_invoice


@pytest.fixture(name="set_redis")
def set_redis() -> Generator:
    with patch("app.controller.redis.set_redis") as set_redis:
        yield set_redis


@pytest.fixture(name="get_redis")
def get_redis() -> Generator:
    with patch("app.controller.redis.get_redis") as get_redis:
        yield get_redis


@pytest.fixture(name="delete_redis")
def delete_redis() -> Generator:
    with patch("app.controller.redis.delete_redis") as delete_redis:
        yield delete_redis


@pytest.fixture(name="bkash_grant_token")
def bkash_grant_token() -> Generator:
    with patch("app.library.bkash.grant_token") as bkash_grant_token:
        yield bkash_grant_token


@pytest.fixture(name="bkash_init_payment")
def bkash_init_payment() -> Generator:
    with patch("app.library.bkash.initiate_payment") as bkash_init_payment:
        yield bkash_init_payment


@pytest.fixture(name="bkash_exec_payment")
def bkash_exec_payment() -> Generator:
    with patch("app.library.bkash.execute_payment") as bkash_exec_payment:
        yield bkash_exec_payment

@pytest.fixture(name="send_email")
def send_email() -> Generator:
    with patch("app.controller.email.FastMail.send_message") as send_email:
        yield send_email

@pytest_asyncio.fixture(name="img_uploader")
async def img_uploader(client: AsyncClient) -> Callable:

    async def _create_image(url: str, headers: dict, mock_upload_file: MagicMock) -> Dict[str, Any]:
        mock_upload_file.return_value = {
            'public_id': 'dummy',
            'secure_url': 'https://res.cloudinary.com/dummy/image/upload/v1631234567/dummy/test.jpg',
            'filename': 'image.jpg'
        }
        with open("dummy/test.jpg", "rb") as f:
            response = await client.post(url,
                                         files=[
                                             ("files", ("image.jpg", f, "image/jpeg"))],
                                         headers=headers
                                         )

        assert response.status_code == status.HTTP_201_CREATED
        mock_upload_file.assert_called_once()

        img = response.json()[0]
        img.pop('public_id')
        img.pop('folder')
        return img

    return _create_image


@pytest_asyncio.fixture(name="book_payload")
def book_payload() -> dict:
    return {
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
    }


@pytest_asyncio.fixture(name="book_in_db")
async def create_book(client: AsyncClient, book_payload: dict, admin_auth_headers: dict):
    response = await client.post("/book", json=book_payload, headers=admin_auth_headers)
    assert response.status_code == status.HTTP_201_CREATED
    return response.json()


@pytest_asyncio.fixture(name="image_in_db")
async def create_image(mock_upload_file: MagicMock, client: AsyncClient, author_in_db: dict, admin_auth_headers: dict):
    mock_upload_file.return_value = {
        'public_id': 'dummy',
        'secure_url': 'https://res.cloudinary.com/dummy/image/upload/v1631234567/dummy/test.jpg',
        'filename': 'image.jpg'
    }

    with open("dummy/test.jpg", "rb") as f:
        response = await client.post("/image/admin?author_id={}".format(author_in_db['id']),
                                     files=[
                                         ("files", ("image.jpg", f, "image/jpeg"))
        ],
            headers=admin_auth_headers)

    assert response.status_code == status.HTTP_201_CREATED
    mock_upload_file.assert_called_once()
    img = response.json()[0]
    img.pop('public_id')
    img.pop('folder')
    return img


@pytest_asyncio.fixture(name="author_payload")
def author_payload() -> dict:
    return {
        "birth_date": "1948-11-13",
        "book_published": 200,
        "city": "dhaka",
        "country": "BD",
        "death_date": "2012-07-19",
        "description": "বাংলাদেশের প্রখ্যাত লেখক",
        "is_popular": True,
        "name": "হুমায়ূন আহমেদ",
        "slug": "humayun-ahmed"
    }


@pytest_asyncio.fixture(name="author_in_db")
async def create_author(client: AsyncClient, author_payload: dict, admin_auth_headers: dict):
    response = await client.post("/author", json=author_payload, headers=admin_auth_headers)
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


@pytest_asyncio.fixture(name="user_payload")
def user_payload() -> dict:
    return {
        "email": "testuser@gmail.com",
        "password": "testPassword2235#",
        "phone_number": "+8801311701123",
        "first_name": "test",
        "last_name": "user",
        "role": "customer"
    }


@pytest_asyncio.fixture(name="user_in_db")
async def create_user_by_admin(client: AsyncClient, user_payload: dict, admin_auth_headers: dict) -> dict[str, dict]:
    response = await client.post("/user", json=user_payload, headers=admin_auth_headers)
    assert response.status_code == status.HTTP_201_CREATED
    user = response.json()
    return {
        'user': user,
        'token': {
            'access_token': create_jwt_token(user['id'], Role.customer, 'access'),
        }
    }


@pytest_asyncio.fixture(name="admin_payload")
def admin_payload() -> dict:
    return {
        "email": "testadmin@gmail.com",
        "password": "testPassword2235#",
        "phone_number": "+8801478639075",
        "first_name": "test",
        "last_name": "user",
        "role": "admin"
    }


@pytest_asyncio.fixture(name="admin_in_db")
async def create_admin_by_admin(client: AsyncClient, admin_payload: dict, admin_auth_headers: dict):
    response = await client.post("/user", json=admin_payload, headers=admin_auth_headers)
    assert response.status_code == status.HTTP_201_CREATED
    return response.json()


@pytest_asyncio.fixture(name="admin_in_db_with_token")
async def create_admin_with_token(client: AsyncClient, admin_in_db: dict, admin_payload: dict):
    response = await client.post('/auth/token', data={"username": admin_in_db['email'], "password": admin_payload['password']})
    assert response.status_code == status.HTTP_200_OK
    access_token = response.json()['access_token']
    return {**admin_in_db, 'token': access_token, 'auth_headers': {'Authorization': f'Bearer {access_token}'}}


@pytest_asyncio.fixture(name="courier_payload")
def courier_payload() -> dict:
    return {
        "method_name": "Delivery Tiger - Inside Dhaka",
        "company_name": "Delivery Tiger",
        "base_charge": 60.0,
        "weight_charge_per_kg": 20.0,
        "allow_cash_on_delivery": True,
        "include_country": ["BD"],
        "include_city": ["dhaka"],
        "exclude_city": [],
    }


@pytest_asyncio.fixture(name="courier_in_db")
async def create_courier(client: AsyncClient, courier_payload: dict, admin_auth_headers: dict):
    response = await client.post("/courier", json=courier_payload, headers=admin_auth_headers)
    assert response.status_code == status.HTTP_201_CREATED
    return response.json()


@pytest_asyncio.fixture(name="address_payload")
def address_payload() -> dict:
    return {
        "name": "test user",
        "phone_number": "+8801710002000",
        "email": "testemail@gmail.com",
        "alternative_phone_number": "+8801710000001",
        "address": "House 1, Road 1, Block A, Dhaka",
        "thana": "dhanmondi",
        "city": "dhaka",
        "country": "BD",
    }


@pytest_asyncio.fixture(name="address_in_db")
async def create_address(client: AsyncClient, address_payload: dict, user_in_db: dict[str, dict]) -> dict[str, dict]:
    response = await client.post("/address", json=address_payload,
                                 headers={"Authorization": "Bearer {}".format(
                                     user_in_db["token"]['access_token'])}
                                 )
    assert response.status_code == status.HTTP_201_CREATED
    return {
        'address': response.json(),
        'user': user_in_db,
    }


@pytest_asyncio.fixture(name="coupon_payload")
def coupon_payload() -> dict:
    return {
        "code": "NewYear",
        "short_description": "New year coupon",
        "expiry_date": "3024-12-10T23:59:59.999999Z",
        "discount_type": "percentage",
        "discount_old": 15,
        "discount_new": 0,
        "min_spend_old": 499,
        "min_spend_new": 0,
    }


@pytest_asyncio.fixture(name="coupon_in_db")
async def create_coupon(client: AsyncClient, coupon_payload: dict, admin_auth_headers: dict):
    response = await client.post("/coupon", json=coupon_payload, headers=admin_auth_headers)
    assert response.status_code == status.HTTP_201_CREATED
    return response.json()


@pytest_asyncio.fixture(name="order_in_db")
async def create_order(send_invoice: MagicMock, client: AsyncClient, book_in_db: dict, admin_auth_headers: dict):
    response = await client.post("/order/admin/new", json={
        "order_items": [
            {
                "book_id": book_in_db["id"],
                "quantity": 1,
            }
        ]
    }, headers=admin_auth_headers)
    assert response.status_code == status.HTTP_201_CREATED
    return response.json()


@pytest_asyncio.fixture(name="payment_gateway_in_db")
async def create_payment_gateway(client: AsyncClient, admin_auth_headers: dict):
    response = await client.post("/payment_gateway", json={
        "name": "bkash",
        "title": "Bkash",
        "is_disabled": False
    }, headers=admin_auth_headers)
    assert response.status_code == status.HTTP_201_CREATED
    return response.json()


@pytest_asyncio.fixture(name="transaction_in_db")
async def create_transaction(client: AsyncClient, book_in_db: dict, payment_gateway_in_db: dict, admin_auth_headers: dict):
    response = await client.post("/order/admin/new", json={
        "order_items": [
            {
                "book_id": book_in_db["id"],
                "quantity": 1,
            }
        ],
        "transactions": [{
            "payment_method": payment_gateway_in_db["name"],
            "amount": 250,
            "transaction_id": "UIOOE98709",
            "account_number": "01710002000",
        }]
    }, headers=admin_auth_headers)
    assert response.status_code == status.HTTP_201_CREATED
    return response.json()["transactions"][0]


@pytest_asyncio.fixture(name="review_payload")
def review_payload() -> dict:
    return {
        "product_rating": 5,
        "time_rating": 5,
        "delivery_rating": 5,
        "website_rating": 5,
        "comment": "Great book I have ever read!"
    }


@pytest_asyncio.fixture(name="review_in_db")
async def create_review(client: AsyncClient, review_payload: dict, book_in_db: dict[str, Any],
                        user_in_db: dict[str, dict], img_uploader: Callable, mock_upload_file: MagicMock):
    headers = {"Authorization": "Bearer {}".format(
        user_in_db["token"]['access_token'])}

    response = await client.post("/review/new", json={
        **review_payload,
        "book_id": book_in_db["id"]
    }, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()

    img = await img_uploader("/image/user?review_id={}".format(data["id"]), headers, mock_upload_file)
    data["images"] = [img]
    data['headers'] = headers

    return data


@pytest_asyncio.fixture(name="customer_access_token")
async def get_access_token() -> str:
    return create_jwt_token(uuid.uuid4(), Role.customer, 'access')


@pytest_asyncio.fixture(name="admin_access_token")
async def get_admin_access_token() -> str:
    return create_jwt_token(uuid.uuid4(), Role.admin, 'access')


@pytest_asyncio.fixture(name='admin_auth_headers')
async def get_admin_auth_headers_with_bearer_token(admin_access_token: str) -> dict:
    return {
        'Authorization': f'Bearer {admin_access_token}'
    }


@pytest_asyncio.fixture(name='customer_auth_headers')
async def get_auth_headers_with_bearer_token(user_in_db: dict[str, dict]) -> dict:
    return {
        'Authorization': f'Bearer {user_in_db["token"]["access_token"]}'
    }


@pytest_asyncio.fixture
def diff() -> Callable:
    def compare(big: dict[str, Any], small: dict[str, Any]) -> None:
        for key, val in small.items():
            if key not in big:
                print(f"Mismatch: {key} not found in greater dict")
            elif isinstance(val, dict):
                print('COMPARING:', key)
                compare(val, big[key])
            elif big[key] != val:
                print("Mismatch: {} | {} | {}".format(key, val, big[key]))

    return compare
