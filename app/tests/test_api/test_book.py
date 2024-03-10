import pytest
import pytest_asyncio
from httpx import AsyncClient
from starlette import status

pytestmark = pytest.mark.asyncio

simple_book = {
    "sku": "99-5432",
    "name": "Test Book",
    "slug": "test-book",
    "regular_price": 100,
    "sale_price": 90,
    "manage_stock": True,
    "quantity": 10,
    "is_used": True,
    "condition": "old like new",
}

@pytest_asyncio.fixture(name="created_book")
async def create_book(client: AsyncClient):
    response = await client.post("/book", json=simple_book)
    assert response.status_code == status.HTTP_201_CREATED
    return response.json()

async def test_get_book_by_id(client: AsyncClient, created_book:dict):
    response = await client.get(f"/book/id/{created_book['id']}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json().items() <= created_book.items()


async def test_get_all_books(client: AsyncClient, created_book:dict):
    response = await client.get("/books")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1
    assert response.json()[0].items() <= created_book.items()
    assert response.headers['x-total-count'] == '1'
    assert response.headers['x-total-pages'] == '1'
    assert response.headers['x-current-page'] == '1'
    assert response.headers['x-per-page'] == '10'
    

async def test_search_books(client: AsyncClient, created_book:dict):
    q = created_book["name"][2:6]
    response = await client.get(f"/book/search/{q}")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1
    assert response.json()[0].items() <= created_book.items()


async def test_create_book(client: AsyncClient):
    response = await client.post("/book", json=simple_book)
    assert response.status_code == status.HTTP_201_CREATED
    assert simple_book.items() <= response.json().items()
    

async def test_update_book(client: AsyncClient, created_book:dict):
    payload = {
        **created_book,
        "name": "Updated Name",
        "quantity": 20,
    }
    response = await client.patch(f"/book/{created_book['id']}", json=payload)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name"] == payload["name"]
    payload.pop('updated_at')
    assert payload.items() <= response.json().items()
    

async def test_delete_book(client: AsyncClient, created_book:dict):
    response = await client.delete(f"/book/{created_book['id']}")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    response = await client.get(f"/book/id/{created_book['id']}")
    assert response.status_code == 404 
      
    
    
