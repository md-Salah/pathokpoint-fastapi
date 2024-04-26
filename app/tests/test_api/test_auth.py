import pytest
from httpx import AsyncClient
from starlette import status
from unittest.mock import patch, AsyncMock
import app.controller.auth as auth_service

pytestmark = pytest.mark.asyncio

simple_user = {
    "email": "testuser@gmail.com",
    "password": "testPassword2235#",
    "phone_number": "+8801311701123",
    "first_name": "test",
    "last_name": "user",
    "username": "testUser1"
}


async def test_user_signup(client: AsyncClient):
    payload = simple_user.copy()
    response = await client.post("/signup", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    payload.pop("password")
    assert response.json()['user'].items() >= payload.items()
    assert response.json()['user']['role'] == "customer"
    assert response.json()['token']['token_type'] == "bearer"


async def test_signup_with_existing_email(client: AsyncClient, user_in_db: dict):
    payload = {
        **simple_user,
        "email": user_in_db['user']['email']
    }
    response = await client.post("/signup", json=payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        "detail": "Email is already registered, Try login or forget password."}


async def test_user_login(client: AsyncClient, user_in_db: dict):
    payload = {
        "username": user_in_db['user']['email'],
        "password": "testPassword2235#"
    }
    response = await client.post("/token", data=payload)

    assert response.status_code == status.HTTP_200_OK
    assert response.json().get("access_token") is not None
    assert response.json().get("token_type") == "bearer"


async def test_user_login_with_wrong_password(client: AsyncClient, user_in_db: dict):
    payload = {
        "username": user_in_db['user']['email'],
        "password": "wrongpassword"
    }
    response = await client.post('/token', data=payload)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()['detail']['message'] == "Incorrect email or password"


async def test_get_private_data(client: AsyncClient, user_in_db: dict):
    token = user_in_db['token']['access_token']
    response = await client.get(
        '/get-private-data', headers={"Authorization": f"Bearer {token}"},)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "message": "You are accessing private data because you have the access token."}


async def test_get_private_data_without_token(client: AsyncClient):
    response = await client.get(
        '/get-private-data'
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Not authenticated"}


@patch("app.api.auth.email_service.send_reset_password_email", new_callable=AsyncMock)
async def test_reset_password(mock_send_email, client: AsyncClient, user_in_db: dict):
    mock_send_email.return_value = {
        "message": "Reset password link has been sent to your email."}

    payload = {"email": user_in_db['user']['email']}
    response = await client.post("/reset-password", json=payload)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "message": "Reset password link has been sent to your email."}

    mock_send_email.assert_awaited_once()


async def test_reset_password_with_wrong_email(client: AsyncClient):
    payload = {"email": "fakeemail@gmail.com"}
    response = await client.post("/reset-password", json=payload)
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_set_new_password(client: AsyncClient, user_in_db: dict):
    reset_token = auth_service.create_jwt_token(
        user_in_db['user']['id'], user_in_db['user']['role'], "reset_password")
    payload = {"token": reset_token, "new_password": "newPassword1234#"}

    response = await client.post("/set-new-password", json=payload)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "message": "Password has been updated successfully."}


async def test_set_new_password_with_wrong_token_type(client: AsyncClient, user_in_db: dict):
    reset_token = auth_service.create_jwt_token(
        user_in_db['user']['id'], user_in_db['user']['role'], "access")
    payload = {"token": reset_token, "new_password": "newPassword1234#"}

    response = await client.post("/set-new-password", json=payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'detail': 'Invalid token'}


@patch("app.api.auth.email_service.send_verification_email", new_callable=AsyncMock)
async def test_request_email_verification(mock_send_email, client: AsyncClient, user_in_db: dict):
    mock_send_email.return_value = {
        "message": "Verification link has been sent to your email."}

    token = user_in_db['token']['access_token']
    response = await client.post("/request-email-verification", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "message": "Verification link has been sent to your email."}

    mock_send_email.assert_awaited_once()


async def test_verify_email(client: AsyncClient, user_in_db: dict):
    token = auth_service.create_jwt_token(
        user_in_db['user']['id'], user_in_db['user']['role'], "verification")
    response = await client.get(f"/verify-email/{token}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Email has been verified successfully."}
    
async def test_verify_email_with_wrong_token_type(client: AsyncClient, user_in_db: dict):
    token = auth_service.create_jwt_token(
        user_in_db['user']['id'], user_in_db['user']['role'], "access")
    response = await client.get(f"/verify-email/{token}")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'detail': 'Invalid token'}