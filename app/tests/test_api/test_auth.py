import pytest
from httpx import AsyncClient
from starlette import status

pytestmark = pytest.mark.asyncio

simple_user = {
    "email": "testuser@gmail.com",
    "password": "testPassword2235#",
    "phone_number": "+8801311701123",
    "first_name": "test",
    "last_name": "user1",
    "username": "lal"
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
    assert response.json() == {"detail": "Incorrect email or password"}


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
