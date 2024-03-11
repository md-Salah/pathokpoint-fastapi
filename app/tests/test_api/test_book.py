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

@pytest_asyncio.fixture(name="book_in_db")
async def create_book(client: AsyncClient):
    response = await client.post("/book", json=simple_book)
    assert response.status_code == status.HTTP_201_CREATED
    return response.json()

async def test_get_book_by_id(client: AsyncClient, book_in_db:dict):
    response = await client.get(f"/book/id/{book_in_db['id']}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json().items() <= book_in_db.items()


async def test_get_all_books(client: AsyncClient, book_in_db:dict):
    response = await client.get("/books")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1
    assert response.json()[0].items() <= book_in_db.items()
    assert response.headers['x-total-count'] == '1'
    assert response.headers['x-total-pages'] == '1'
    assert response.headers['x-current-page'] == '1'
    assert response.headers['x-per-page'] == '10'
    

async def test_search_books(client: AsyncClient, book_in_db:dict):
    q = book_in_db["name"][2:6]
    response = await client.get(f"/book/search/{q}")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1
    assert response.json()[0].items() <= book_in_db.items()


async def test_create_book(client: AsyncClient):
    response = await client.post("/book", json=simple_book)
    assert response.status_code == status.HTTP_201_CREATED
    assert simple_book.items() <= response.json().items()
    
async def test_create_book_with_author(client: AsyncClient, author_in_db:dict):
    payload = {
        **simple_book,
        "authors": [author_in_db['id']]
    }
    response = await client.post("/book", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    assert simple_book.items() <= response.json().items()
    assert response.json()["authors"][0] == author_in_db
    
async def test_create_book_with_publisher(client: AsyncClient, publisher_in_db:dict):
    payload = {
        **simple_book,
        "publisher": publisher_in_db["id"]
    }
    response = await client.post("/book", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    assert simple_book.items() <= response.json().items()
    assert response.json()["publisher"] == publisher_in_db

async def test_create_book_with_category(client: AsyncClient, category_in_db:dict):
    payload = {
        **simple_book,
        "categories": [category_in_db['id']]
    }
    response = await client.post("/book", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    assert simple_book.items() <= response.json().items()
    assert response.json()["categories"][0] == category_in_db

async def test_update_book(client: AsyncClient, book_in_db:dict):
    payload = {
        **book_in_db,
        "name": "Updated Name",
        "quantity": 20,
    }
    response = await client.patch(f"/book/{book_in_db['id']}", json=payload)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name"] == payload["name"]
    payload.pop('updated_at')
    assert payload.items() <= response.json().items()
    

async def test_delete_book(client: AsyncClient, book_in_db:dict):
    response = await client.delete(f"/book/{book_in_db['id']}")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    response = await client.get(f"/book/id/{book_in_db['id']}")
    assert response.status_code == 404 
      
    
    
