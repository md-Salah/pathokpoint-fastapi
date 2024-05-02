import pytest
from httpx import AsyncClient
from starlette import status
from unittest.mock import patch, AsyncMock
import json

import app.controller.auth as auth_service
from app.constant.role import Role

pytestmark = pytest.mark.asyncio

simple_user = {
    "email": "testuser@gmail.com",
    "password": "testPassword2235#",
    "phone_number": "+8801311701123",
    "first_name": "test",
    "last_name": "user",
    "username": "testUser1"
}


@pytest.fixture
def send_signup_otp():
    with patch("app.api.auth.email_service.send_signup_otp") as send_signup_otp:
        yield send_signup_otp

@pytest.fixture
def send_reset_password_otp():
    with patch("app.api.auth.email_service.send_reset_password_otp") as send_reset_password_otp:
        yield send_reset_password_otp

@pytest.fixture
def set_redis():
    with patch("app.api.auth.set_redis") as set_redis:
        yield set_redis


@pytest.fixture
def get_redis():
    with patch("app.api.auth.get_redis") as get_redis:
        yield get_redis


async def test_user_signup(send_signup_otp, set_redis, get_redis, client: AsyncClient):
    send_signup_otp.return_value = None
    set_redis.return_value = None
    payload = simple_user.copy()
    response = await client.post("/auth/signup", json=payload)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['detail'] == {
        "message": "OTP has been sent to your email. Please verify within {} minutes.".format(10)}

    # Verify OTP
    get_redis.return_value = json.dumps({
        'payload': payload,
        'otp': '123456'
    })
    response = await client.post("/auth/verify-otp", json={
        'email': payload['email'],
        'otp': '123456'
    })
    assert response.status_code == status.HTTP_201_CREATED
    payload.pop('password')
    assert response.json().items() >= payload.items()


async def test_user_signup_with_wrong_otp(client: AsyncClient, get_redis):
    get_redis.return_value = json.dumps({
        'payload': simple_user,
        'otp': '123456'
    })
    response = await client.post("/auth/verify-otp", json={
        'email': simple_user['email'],
        'otp': '654321'
    })
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()['detail']['message'] == "Invalid OTP, Try again."


async def test_signup_with_existing_email(client: AsyncClient, user_in_db: dict):
    payload = {
        **simple_user,
        "email": user_in_db['user']['email']
    }
    response = await client.post("/auth/signup", json=payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()[
        'detail']['message'] == "Email is already registered, Try login or forget password."


async def test_user_login(client: AsyncClient, user_in_db: dict):
    payload = {
        "username": user_in_db['user']['email'],
        "password": "testPassword2235#"
    }
    response = await client.post("/auth/token", data=payload)

    assert response.status_code == status.HTTP_200_OK
    assert response.json().get("access_token") is not None
    assert response.json().get("token_type") == "bearer"


async def test_user_login_with_wrong_password(client: AsyncClient, user_in_db: dict):
    payload = {
        "username": user_in_db['user']['email'],
        "password": "wrongpassword"
    }
    response = await client.post('/auth/token', data=payload)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()[
        'detail']['message'] == "Incorrect email or password"


async def test_get_private_data(client: AsyncClient, user_in_db: dict):
    token = user_in_db['token']['access_token']
    response = await client.get(
        '/auth/get-private-data', headers={"Authorization": f"Bearer {token}"},)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "message": "You are accessing private data because you have the access token."}


async def test_get_private_data_without_token(client: AsyncClient):
    response = await client.get(
        '/auth/get-private-data'
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Not authenticated"}


async def test_reset_password(send_reset_password_otp, set_redis, client: AsyncClient, user_in_db: dict):
    send_reset_password_otp.return_value = None
    set_redis.return_value = None
    
    payload = {"email": user_in_db['user']['email']}
    response = await client.post("/auth/reset-password", json=payload)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['detail']['message'] == "OTP has been sent to your email. Please reset your password within {} minutes.".format(10)



async def test_set_new_password(get_redis, client: AsyncClient, user_in_db: dict):
    get_redis.return_value = "123456"
    
    payload = {"otp": "123456", 'email': user_in_db['user']['email'], "new_password": "newPassword1234#"}

    response = await client.post("/auth/set-new-password", json=payload)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "message": "Password has been updated successfully."}
    
    # Login with new password
    payload = {
        "username": user_in_db['user']['email'],
        "password": "newPassword1234#"
    }
    response = await client.post('/auth/token', data=payload)
    assert response.status_code == status.HTTP_200_OK
    assert response.json().get("access_token") is not None
    
async def test_reset_password_with_wrong_email(client: AsyncClient):
    payload = {"email": "fakeemail@gmail.com"}
    response = await client.post("/auth/reset-password", json=payload)
    assert response.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.parametrize("otp, msg", [
    ("123456", "Invalid OTP, Try again."),
    ("", "OTP expired, Try again.")
])
async def test_set_new_password_with_wrong_otp(get_redis, client: AsyncClient, user_in_db: dict, otp: str, msg: str):
    get_redis.return_value = otp
    payload = {"otp": "654321", 'email': user_in_db['user']['email'], "new_password": "newPassword1234#"}
    
    response = await client.post("/auth/set-new-password", json=payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()['detail']['message'] == msg
    
