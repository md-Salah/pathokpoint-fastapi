import pytest
import pytest_asyncio
from httpx import AsyncClient
from starlette import status

pytestmark = pytest.mark.asyncio

simple_address = {
        "phone_number": "01710000000",
        "alternative_phone_number": "01710000001",
        "address": "House 1, Road 1, Block A, Dhaka",
        "thana": "dhanmondi",
        "city": "dhaka",
        "country": "bangladesh",
    }

simple_user = {
        "email": "testuser@gmail.com",
        "first_name": "Fname",
        "last_name": "Lname",
        "password": "test123456",
        "phone_number": "017xxxxxxxx",
        "username": "testuser"
    }

@pytest_asyncio.fixture(name="user")
async def create_user(client: AsyncClient):
    response = await client.post("/signup", json=simple_user)
    assert response.status_code == status.HTTP_201_CREATED
    return response.json()

@pytest_asyncio.fixture(name="created_address")
async def create_address(client: AsyncClient, user: dict):
    response = await client.post(f"/address/{user['user']['id']}", json=simple_address)
    assert response.status_code == status.HTTP_201_CREATED
    return response.json()

# GET /address/id/{id}
async def test_get_address_by_id(client: AsyncClient, created_address: dict):
    response = await client.get(f"/address/id/{created_address['id']}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json().items() >= created_address.items()
    
# GET /address/id/{id}
async def test_get_address_by_fake_id(client: AsyncClient):
    id = 'some-fake-id'
    response = await client.get(f"/address/id/{id}")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json()['detail'][0]['loc'][1] == 'id'
    assert 'Input should be a valid UUID' in response.json()['detail'][0]['msg']
    
    
# GET /address/id/{id}
async def test_get_address_by_fake_uuid(client: AsyncClient):
    id = '123e4567-e89b-12d3-a456-426614174000'
    response = await client.get(f"/address/id/{id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': f'Address with id ({id}) not found'}


# GET /addresss
async def test_get_all_addresss(client: AsyncClient, created_address: dict):
    response = await client.get(f"/addresss/{created_address['user_id']}")
    assert len(response.json()) == 1
    assert response.json()[0].items() >= simple_address.items()
    
# POST /address
async def test_create_address(client: AsyncClient, user: dict):
    response = await client.post(f"/address/{user['user']['id']}", json=simple_address)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json().items() >= simple_address.items()

    
# PATCH /address/{id}
async def test_update_address(client: AsyncClient, created_address: dict):
    created_address['city'] = 'chattogram'
    created_address.pop('updated_at')
    response = await client.patch(f"/address/{created_address['id']}", json=created_address)
    assert response.status_code == status.HTTP_200_OK
    assert response.json().items() >= created_address.items()

# DELETE /address/{id}
async def test_delete_address(client: AsyncClient, created_address: dict):
    id = created_address['id']
    response = await client.delete(f"/address/{id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    response = await client.get(f"/address/id/{id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND
      
    
    
