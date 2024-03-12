import pytest
import pytest_asyncio
from httpx import AsyncClient
from starlette import status

pytestmark = pytest.mark.asyncio

simple_coupon = {
    "code": "free-delivery",
    "short_description": "Free Delivery Coupon",
    "expiry_date": "2024-12-31T00:00:00",
    "discount_type": "percentage",
    "discount_old": 15,
    "discount_new": 0,
    "min_spend_old": 499,
    "min_spend_new": 0,
}

@pytest_asyncio.fixture(name="coupon_in_db")
async def create_coupon(client: AsyncClient):
    response = await client.post("/coupon", json=simple_coupon)
    assert response.status_code == status.HTTP_201_CREATED
    return response.json()

async def test_get_coupon_by_id(client: AsyncClient, coupon_in_db:dict):
    response = await client.get(f"/coupon/id/{coupon_in_db['id']}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json().items() <= coupon_in_db.items()


async def test_get_all_coupons(client: AsyncClient, coupon_in_db:dict):
    response = await client.get("/coupons")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1
    assert response.json()[0].items() <= coupon_in_db.items()
    assert response.headers['x-total-count'] == '1'
    assert response.headers['x-total-pages'] == '1'
    assert response.headers['x-current-page'] == '1'
    assert response.headers['x-per-page'] == '10'
    

async def test_create_coupon(client: AsyncClient):
    response = await client.post("/coupon", json=simple_coupon)
    assert response.status_code == status.HTTP_201_CREATED
    assert simple_coupon.items() <= response.json().items()
    
async def test_create_coupon_with_author(client: AsyncClient, author_in_db:dict):
    payload = {
        **simple_coupon,
        "include_authors": [author_in_db['id']]
    }
    response = await client.post("/coupon", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    assert simple_coupon.items() <= response.json().items()
    assert response.json()["include_authors"][0] == author_in_db
    
async def test_create_coupon_with_publisher(client: AsyncClient, publisher_in_db:dict):
    payload = {
        **simple_coupon,
        "include_publishers": [publisher_in_db["id"]]
    }
    response = await client.post("/coupon", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    assert simple_coupon.items() <= response.json().items()
    assert response.json()["include_publishers"][0] == publisher_in_db

async def test_create_coupon_with_category(client: AsyncClient, category_in_db:dict):
    payload = {
        **simple_coupon,
        "include_categories": [category_in_db['id']]
    }
    response = await client.post("/coupon", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    assert simple_coupon.items() <= response.json().items()
    assert response.json()["include_categories"][0] == category_in_db
    
async def test_create_coupon_with_exclude_category(client: AsyncClient, category_in_db:dict):
    payload = {
        **simple_coupon,
        "exclude_categories": [category_in_db['id']]
    }
    response = await client.post("/coupon", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    assert simple_coupon.items() <= response.json().items()
    assert response.json()["exclude_categories"][0] == category_in_db

async def test_update_coupon(client: AsyncClient, coupon_in_db:dict):
    payload = {
        **coupon_in_db,
        "expiry_date": "2025-12-31T00:00:00",
    }
    response = await client.patch(f"/coupon/{coupon_in_db['id']}", json=payload)
    assert response.status_code == status.HTTP_200_OK
    payload.pop('updated_at')
    assert payload.items() <= response.json().items()
    

async def test_delete_coupon(client: AsyncClient, coupon_in_db:dict):
    response = await client.delete(f"/coupon/{coupon_in_db['id']}")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    response = await client.get(f"/coupon/id/{coupon_in_db['id']}")
    assert response.status_code == 404 
      
    
    
