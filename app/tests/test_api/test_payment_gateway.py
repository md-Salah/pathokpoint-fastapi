import pytest
from httpx import AsyncClient
from starlette import status

pytestmark = pytest.mark.asyncio

simple_payment_gateway = {
    "name": "Bkash",
    "description": "Bkash Payment Gateway",
    "is_enabled": True
}


async def test_get_payment_gateway_by_id(client: AsyncClient, payment_gateway_in_db: dict):
    response = await client.get(f"/payment_gateway/id/{payment_gateway_in_db['id']}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json().items() >= payment_gateway_in_db.items()


async def test_get_payment_gateway_by_fake_id(client: AsyncClient):
    id = 'some-fake-id'
    response = await client.get(f"/payment_gateway/id/{id}")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json()['detail'][0]['loc'][1] == 'id'
    assert 'Input should be a valid UUID' in response.json()[
        'detail'][0]['msg']


async def test_get_all_payment_gateways(client: AsyncClient, payment_gateway_in_db: dict):
    response = await client.get("/payment_gateways")
    assert len(response.json()) == 1
    assert response.json()[0].items() >= simple_payment_gateway.items()


async def test_create_payment_gateway(client: AsyncClient):
    response = await client.post("/payment_gateway", json=simple_payment_gateway)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json().items() >= simple_payment_gateway.items()


async def test_create_duplicate_payment_gateway(client: AsyncClient, payment_gateway_in_db: dict):
    response = await client.post("/payment_gateway", json=simple_payment_gateway)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'detail': 'PaymentGateway with method name ({}) already exists'.format(
        simple_payment_gateway["name"])}


async def test_update_payment_gateway(client: AsyncClient, payment_gateway_in_db: dict):
    payment_gateway_in_db['is_enabled'] = False
    payment_gateway_in_db.pop('updated_at')
    response = await client.patch(f"/payment_gateway/{payment_gateway_in_db['id']}", json=payment_gateway_in_db)
    assert response.status_code == status.HTTP_200_OK
    assert response.json().items() >= payment_gateway_in_db.items()


async def test_delete_payment_gateway(client: AsyncClient, payment_gateway_in_db: dict):
    id = payment_gateway_in_db['id']
    response = await client.delete(f"/payment_gateway/{id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    response = await client.get(f"/payment_gateway/id/{id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND
