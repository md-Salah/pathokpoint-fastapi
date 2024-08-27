import pytest
from httpx import AsyncClient
from starlette import status
from typing import Any

pytestmark = pytest.mark.asyncio

simple_address = {
    'name': 'John Doe',
    "phone_number": "+8801710002000",
    "alternative_phone_number": "+8801710000001",
    "address": "House 1, Road 1, Block A, Dhaka",
    "thana": "dhanmondi",
    "city": "dhaka",
    "country": "BD",
}


async def test_get_address_by_id(client: AsyncClient, address_in_db: dict[str, Any]):
    headers = {"Authorization": "Bearer {}".format(
        address_in_db['user']['token']['access_token'])}
    response = await client.get(f"/address/id/{address_in_db['address']['id']}", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json().items() >= address_in_db['address'].items()


async def test_get_address_by_id_by_admin(client: AsyncClient, address_in_db: dict[str, Any], admin_auth_headers: dict):
    response = await client.get(f"/address/id/{address_in_db['address']['id']}", headers=admin_auth_headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json().items() >= address_in_db['address'].items()


async def test_get_all_addresses_by_user_id(client: AsyncClient, address_in_db: dict[str, Any]):
    headers = {"Authorization": "Bearer {}".format(
        address_in_db['user']['token']['access_token'])}
    response = await client.get("/address/user/{}/all".format(address_in_db['user']['user']['id']), headers=headers)
    assert len(response.json()) == 1
    assert response.json()[0].items() >= address_in_db['address'].items()


async def test_create_address(client: AsyncClient, user_in_db: dict[str, Any]):
    payload = simple_address.copy()
    response = await client.post("/address", json=payload,
                                 headers={'Authorization': "Bearer {}".format(
                                     user_in_db['token']['access_token'])}
                                 )
    # assert response.status_code == status.HTTP_201_CREATED
    assert response.json().items() >= payload.items()


async def test_update_address(client: AsyncClient, address_in_db: dict[str, Any]):
    payload = {
        'city': 'feni'
    }
    response = await client.patch(f"/address/{address_in_db['address']['id']}", json=payload, headers={
        'Authorization': "Bearer {}".format(address_in_db['user']['token']['access_token'])
    })
    assert response.status_code == status.HTTP_200_OK
    address_in_db['address'].update(payload)
    address_in_db['address'].pop('updated_at')
    assert response.json().items() >= address_in_db['address'].items()


async def test_delete_my_address(client: AsyncClient, address_in_db: dict[str, Any]):
    response = await client.delete("/address/{}".format(address_in_db['address']['id']), headers={
        'Authorization': "Bearer {}".format(address_in_db['user']['token']['access_token'])
    })
    assert response.status_code == status.HTTP_204_NO_CONTENT


async def test_delete_address_by_admin(client: AsyncClient, address_in_db: dict[str, Any], admin_auth_headers: dict):
    response = await client.delete("/address/{}".format(address_in_db['address']['id']), headers=admin_auth_headers)
    assert response.status_code == status.HTTP_204_NO_CONTENT


async def test_delete_address_by_other_customer(client: AsyncClient, address_in_db: dict[str, Any], customer_access_token: str):
    response = await client.delete("/address/{}".format(address_in_db['address']['id']), headers={
        'Authorization': "Bearer {}".format(customer_access_token)
    })
    assert response.status_code == status.HTTP_403_FORBIDDEN
