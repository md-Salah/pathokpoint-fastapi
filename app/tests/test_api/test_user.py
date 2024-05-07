import pytest
from httpx import AsyncClient
from starlette import status

pytestmark = pytest.mark.asyncio

simple_user = {
    "email": "testuser@gmail.com",
    "password": "testPassword2235#",
    "phone_number": "+8801311701123",
    "first_name": "test",
    "last_name": "user"
}


async def test_get_user_by_id(client: AsyncClient, user_in_db: dict, admin_auth_headers: dict):
    id = user_in_db['user']['id']
    response = await client.get(f"/user/id/{id}", headers=admin_auth_headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json().items() >= user_in_db['user'].items()


@pytest.mark.parametrize(
    "query_param, expected_count, modify_query_string",
    [
        ("", 1, lambda qs, _: qs),
        ("q={}", 1, lambda qs, user: qs.format(user['phone_number'][2:])),
        ("username={}", 1, lambda qs, user: qs.format(user['username'])),
        ("email={}", 1, lambda qs, user: qs.format(user['email'])),
        ("phone_number={}", 1, lambda qs, user: qs.format(
            user['phone_number'].replace('+', '%2B'))),
        ("role=admin", 0, lambda qs, _: qs),
        ("role=customer", 1, lambda qs, _: qs),
    ]
)
async def test_get_all_users_by_admin(client: AsyncClient, user_in_db: dict, admin_auth_headers: dict, query_param: str, expected_count: int, modify_query_string):
    query = modify_query_string(query_param, user_in_db['user'])
    response = await client.get(f"/user/all?{query}", headers=admin_auth_headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.headers['X-Total-Count'] == str(expected_count)
    assert len(response.json()) == expected_count


async def test_create_user_by_admin(client: AsyncClient, admin_auth_headers: dict):
    payload = simple_user.copy()
    response = await client.post("/user", json=payload, headers=admin_auth_headers)
    assert response.status_code == status.HTTP_201_CREATED
    payload.pop('password')
    assert response.json().items() >= payload.items()


async def test_update_me(client: AsyncClient, user_in_db: dict):
    payload = {
        'first_name': 'updated first name',
    }
    response = await client.patch("/user/me", json=payload,
                                  headers={'Authorization': f"Bearer {user_in_db['token']['access_token']}"})
    assert response.status_code == status.HTTP_200_OK
    user_in_db['user']['first_name'] = payload['first_name']
    user_in_db['user']['updated_at'] = response.json()['updated_at']
    assert response.json().items() >= user_in_db['user'].items()


async def test_update_user_by_admin(client: AsyncClient, user_in_db: dict, admin_auth_headers: dict):
    payload = {
        'first_name': 'updated first name',
        'role': 'admin'
    }
    response = await client.patch(f"/user/id/{user_in_db['user']['id']}", json=payload, headers=admin_auth_headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json().items() >= payload.items()


async def test_delete_me(client: AsyncClient, user_in_db: dict):
    headers = {"Authorization":
               "Bearer {}".format(user_in_db['token']['access_token'])}
    response = await client.delete("/user/me", headers=headers)
    assert response.status_code == status.HTTP_204_NO_CONTENT


async def test_delete_user_by_admin(client: AsyncClient, user_in_db: dict, admin_auth_headers: dict):
    response = await client.delete(f"/user/id/{user_in_db['user']['id']}", headers=admin_auth_headers)
    assert response.status_code == status.HTTP_204_NO_CONTENT
