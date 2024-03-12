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

async def test_get_user_by_id(client: AsyncClient, user_in_db: dict):
    id = user_in_db['user']['id']
    response = await client.get(f"/user/id/{id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json().items() >= user_in_db['user'].items()

async def test_get_all_users(client: AsyncClient, user_in_db: dict):
    response = await client.get("/users")
    assert len(response.json()) == 1
    assert response.json()[0].items() >= user_in_db['user'].items()


async def test_create_user(client: AsyncClient):
    payload = simple_user.copy()
    response = await client.post("/user", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    payload.pop('password')
    assert response.json().items() >= payload.items()


async def test_update_user(client: AsyncClient, user_in_db: dict):
    payload = {
        'first_name': 'updated first name',
    }
    response = await client.patch(f"/user/{user_in_db['user']['id']}", json=payload)
    assert response.status_code == status.HTTP_200_OK
    assert response.json().items() >= payload.items()


async def test_delete_user(client: AsyncClient, user_in_db: dict):
    id = user_in_db['user']['id']
    response = await client.delete(f"/user/{id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    response = await client.get(f"/user/id/{id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND
