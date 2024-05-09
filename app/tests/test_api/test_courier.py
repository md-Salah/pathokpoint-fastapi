import pytest
from httpx import AsyncClient
from starlette import status

pytestmark = pytest.mark.asyncio

simple_courier = {
    "method_name": "Delivery Tiger - Inside Dhaka",
    "company_name": "Delivery Tiger",
    "base_charge": 60.0,
    "weight_charge_per_kg": 20.0,
    "allow_cash_on_delivery": True,
    "include_country": ["BD"],
    "include_city": ["dhaka"],
    "exclude_city": [],
}


async def test_get_courier_by_id(client: AsyncClient, courier_in_db: dict):
    response = await client.get(f"/courier/id/{courier_in_db['id']}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json().items() >= courier_in_db.items()


async def test_get_all_couriers(client: AsyncClient, courier_in_db: dict):
    response = await client.get("/courier/all")
    assert len(response.json()) == 1
    assert response.json()[0].items() >= simple_courier.items()


async def test_create_courier(client: AsyncClient, admin_auth_headers: dict):
    response = await client.post("/courier", json=simple_courier, headers=admin_auth_headers)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json().items() >= simple_courier.items()


async def test_create_duplicate_courier(client: AsyncClient, courier_in_db: dict, admin_auth_headers: dict):
    response = await client.post("/courier", json=courier_in_db, headers=admin_auth_headers)
    assert response.status_code == status.HTTP_409_CONFLICT


async def test_update_courier(client: AsyncClient, courier_in_db: dict, admin_auth_headers: dict):
    payload = {
        'base_charge': 130
    }
    response = await client.patch(f"/courier/{courier_in_db['id']}", json=payload, headers=admin_auth_headers)
    assert response.status_code == status.HTTP_200_OK
    courier_in_db.update(payload)
    courier_in_db.pop('updated_at')
    assert response.json().items() >= courier_in_db.items()


async def test_delete_courier(client: AsyncClient, courier_in_db: dict, admin_auth_headers: dict):
    response = await client.delete("/courier/{}".format(courier_in_db['id']), headers=admin_auth_headers)
    assert response.status_code == status.HTTP_204_NO_CONTENT
