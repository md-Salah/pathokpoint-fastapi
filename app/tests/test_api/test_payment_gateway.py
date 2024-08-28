import pytest
from httpx import AsyncClient
from starlette import status

pytestmark = pytest.mark.asyncio

simple_payment_gateway = {
    "name": "bkash",
    "title": "Bkash",
    "is_disabled": False,
    "is_admin_only": False,
}


async def test_get_payment_gateway_by_id(client: AsyncClient, payment_gateway_in_db: dict, admin_auth_headers: dict):
    response = await client.get(f"/payment_gateway/id/{payment_gateway_in_db['id']}", headers=admin_auth_headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json().items() >= payment_gateway_in_db.items()


async def test_get_all_payment_gateways(client: AsyncClient, payment_gateway_in_db: dict, admin_auth_headers: dict):
    response = await client.get("/payment_gateway/all", headers=admin_auth_headers)
    assert len(response.json()) == 1
    assert response.json()[0].items() >= simple_payment_gateway.items()


async def test_create_payment_gateway(client: AsyncClient, admin_auth_headers: dict):
    response = await client.post("/payment_gateway", json=simple_payment_gateway, headers=admin_auth_headers)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json().items() >= simple_payment_gateway.items()


async def test_create_duplicate_payment_gateway(client: AsyncClient, payment_gateway_in_db: dict, admin_auth_headers: dict):
    response = await client.post("/payment_gateway", json=simple_payment_gateway, headers=admin_auth_headers)
    assert response.status_code == status.HTTP_409_CONFLICT


async def test_update_payment_gateway(client: AsyncClient, payment_gateway_in_db: dict, admin_auth_headers: dict):
    payload = {
        'is_disabled': True
    }
    response = await client.patch(f"/payment_gateway/{payment_gateway_in_db['id']}", json=payload, headers=admin_auth_headers)
    assert response.status_code == status.HTTP_200_OK
    payment_gateway_in_db.pop('updated_at')
    payment_gateway_in_db.update(payload)
    assert response.json().items() >= payment_gateway_in_db.items()


async def test_delete_payment_gateway(client: AsyncClient, payment_gateway_in_db: dict, admin_auth_headers: dict):
    response = await client.delete("/payment_gateway/{}".format(payment_gateway_in_db['id']), headers=admin_auth_headers)
    assert response.status_code == status.HTTP_204_NO_CONTENT
