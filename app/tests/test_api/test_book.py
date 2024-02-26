import pytest
from httpx import AsyncClient
from starlette import status

pytestmark = pytest.mark.asyncio

async def create_book(payload: dict, client: AsyncClient):
    return await client.post("/book", json=payload)

# GET /book/id/{id}
async def test_get_book_by_id(client: AsyncClient):
    payload = {
        "name": "Test Book",
        "regular_price": 100
    }
    response = await create_book(payload, client)
    response = await client.get(f"/book/id/{response.json()['id']}")
    data = response.json()
    assert response.status_code == 200
    assert data["name"] == "Test Book"
    
# GET /book/slug/{slug}
async def test_get_book_by_slug(client: AsyncClient):
    payload = {
        "name": "Test Book by Slug",
        "regular_price": 100
    }
    response = await create_book(payload, client)
    data = response.json()
    response = await client.get(f"/book/slug/{data['slug']}")
    data = response.json()
    assert response.status_code == 200
    assert data["name"] == "Test Book by Slug" 

# GET /books
async def test_get_all_books(client: AsyncClient):
    payload = {
        "name": "Test Book",
        "regular_price": 100
    }
    await create_book(payload, client)
    response = await client.get("/books")
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Test Book"
    
# GET /book/search/{q}
async def test_search_books(client: AsyncClient):
    payload = {
        "name": "Test Book",
        "regular_price": 100
    }
    await create_book(payload, client)
    response = await client.get("/book/search/Test")
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Test Book"
    
    response = await client.get("/book/search/Book")
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Test Book"
    

# POST /book
async def test_create_book(client: AsyncClient):
    payload = {
        "name": "Test Book",
        "regular_price": 100
    }
    response = await client.post("/book", json=payload)
    data = response.json()
    assert response.status_code == 201
    assert data["name"] == "Test Book"
    # Test the slug is generated
    assert data['slug'] == 'test-book'
    
# PATCH /book/{id}
async def test_update_book(client: AsyncClient):
    payload = {
        "name": "Test Book",
        "regular_price": 100
    }
    response = await create_book(payload, client)
    data = response.json()
    payload = {
        "name": "Updated Book",
    }
    response = await client.patch(f"/book/{data['id']}", json=payload)
    data = response.json()
    assert response.status_code == 200
    assert data["name"] == "Updated Book"
    assert data["regular_price"] == 100

# DELETE /book/{id}
async def test_delete_book(client: AsyncClient):
    payload = {
        "name": "Test Delete Book",
        "regular_price": 100
    }
    response = await create_book(payload, client)
    id = response.json()['id']
    
    response = await client.delete(f"/book/{id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # check if the book exists yet
    response = await client.get(f"/book/id/{id}")
    assert response.status_code == 404 
      
    
    
