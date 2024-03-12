import pytest
import pytest_asyncio
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


@pytest_asyncio.fixture(name="courier_in_db")
async def create_courier(client: AsyncClient):
    response = await client.post("/courier", json=simple_courier)
    assert response.status_code == status.HTTP_201_CREATED
    return response.json()


async def test_get_courier_by_id(client: AsyncClient, courier_in_db: dict):
    response = await client.get(f"/courier/id/{courier_in_db['id']}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json().items() >= courier_in_db.items()


async def test_get_courier_by_fake_id(client: AsyncClient):
    id = 'some-fake-id'
    response = await client.get(f"/courier/id/{id}")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json()['detail'][0]['loc'][1] == 'id'
    assert 'Input should be a valid UUID' in response.json()[
        'detail'][0]['msg']


async def test_get_courier_by_fake_uuid(client: AsyncClient):
    id = '123e4567-e89b-12d3-a456-426614174000'
    response = await client.get(f"/courier/id/{id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': f'Courier with id ({id}) not found'}


async def test_get_all_couriers(client: AsyncClient, courier_in_db: dict):
    response = await client.get("/couriers")
    assert len(response.json()) == 1
    assert response.json()[0].items() >= simple_courier.items()


async def test_create_courier(client: AsyncClient):
    response = await client.post("/courier", json=simple_courier)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json().items() >= simple_courier.items()


async def test_create_duplicate_courier(client: AsyncClient, courier_in_db: dict):
    response = await client.post("/courier", json=simple_courier)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'detail': f'Courier with method name ({
        simple_courier["method_name"]}) already exists'}


async def test_update_courier(client: AsyncClient, courier_in_db: dict):
    courier_in_db['base_charge'] = 100.0
    courier_in_db.pop('updated_at')
    response = await client.patch(f"/courier/{courier_in_db['id']}", json=courier_in_db)
    assert response.status_code == status.HTTP_200_OK
    assert response.json().items() >= courier_in_db.items()


async def test_delete_courier(client: AsyncClient, courier_in_db: dict):
    id = courier_in_db['id']
    response = await client.delete(f"/courier/{id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    response = await client.get(f"/courier/id/{id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND
