import pytest
from httpx import AsyncClient
from starlette import status

pytestmark = pytest.mark.asyncio

async def create_user(payload: dict, client: AsyncClient):
    response = await client.post(
        "/signup", json=payload
    )
    return response
    
# /signup
async def test_user_signup(client: AsyncClient):  
    payload = {
        "email": "testuser@gmail.com",
        "password": "testPassword2235#",
        "phone_number": "+8801311701123",
        "first_name": "test",
        "last_name": "user1",
        "username": "lal"
    } 
     
    response = await client.post(
        "/signup", json=payload
    )
    data = response.json()
    user = data['user']
    token = data['token']

    payload.pop('password')
    payload.pop('username')
    assert response.status_code == status.HTTP_201_CREATED
    assert payload.items() <= user.items()
    assert user['role'] == "customer"
    assert token['token_type'] == "bearer"

async def test_signup_with_existing_email(client: AsyncClient):
    payload = {
        "first_name": "test",
        "last_name": "user1",
        "email": "existingemail@gmail.com",
        "password": "testPassword2235#",
    }
    await create_user(payload, client)
    
    response = await client.post(
        "/signup", json=payload
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Email is already registered, Try login or forget password."}    
    
# /token
async def test_user_login(client: AsyncClient):
    payload = {
        "email": "testuser@gmail.com",
        "password": "testPassword2235#",
        "first_name": "test",
        "last_name": "user1",
    } 
    
    await create_user(payload, client)
    
    response = await client.post(
        "/token", data={"username": payload['email'], "password": payload['password']}
    )
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json().get("access_token") is not None
    assert response.json().get("token_type") == "bearer"
    
async def test_user_login_with_wrong_password(client: AsyncClient):
    payload = {
        "email": "testuser@gmail.com",
        "password": "testPassword2235#",
        "first_name": "test",
        "last_name": "user1",
    }
    
    await create_user(payload, client)
    
    response = await client.post(
        '/token', data={"username": payload['email'], "password": "wrongpassword"}
    )
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Incorrect email or password"}
    
# /get-private-data
async def test_get_private_data(client: AsyncClient):
    payload = {
        "email": "testuser@gmail.com",
        "password": "testPassword2235#",
        "first_name": "test",
        "last_name": "user1",
    } 
    
    response = await create_user(payload, client)
    token = response.json()['token']['access_token']
    
    response = await client.get(
        '/get-private-data', headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "You are accessing private data because you have the access token."}
    
async def test_get_private_data_without_token(client: AsyncClient):
    response = await client.get(
        '/get-private-data'
    )
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Not authenticated"}