import pytest
from httpx import AsyncClient
from starlette import status

pytestmark = pytest.mark.asyncio

simple_address = {
    "phone_number": "+8801710002000",
    "alternative_phone_number": "+8801710000001",
    "address": "House 1, Road 1, Block A, Dhaka",
    "thana": "dhanmondi",
    "city": "dhaka",
    "country": "BD",
}

async def test_get_address_by_id(client: AsyncClient, address_in_db: dict):
    response = await client.get(f"/address/id/{address_in_db['id']}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json().items() >= address_in_db.items()


async def test_get_all_addresss(client: AsyncClient, address_in_db: dict):
    response = await client.get(f"/addresss/{address_in_db['user_id']}")
    assert len(response.json()) == 1
    assert response.json()[0].items() >= simple_address.items()


async def test_create_address(client: AsyncClient, user_in_db: dict):
    response = await client.post(f"/address/{user_in_db['user']['id']}", json=simple_address)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json().items() >= simple_address.items()


async def test_update_address(client: AsyncClient, address_in_db: dict):
    address_in_db['city'] = 'chattogram'
    address_in_db.pop('updated_at')
    response = await client.patch(f"/address/{address_in_db['id']}", json=address_in_db)
    assert response.status_code == status.HTTP_200_OK
    assert response.json().items() >= address_in_db.items()


async def test_delete_address(client: AsyncClient, address_in_db: dict):
    id = address_in_db['id']
    response = await client.delete(f"/address/{id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    response = await client.get(f"/address/id/{id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND
