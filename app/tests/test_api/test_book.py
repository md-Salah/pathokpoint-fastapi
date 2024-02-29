import pytest
from httpx import AsyncClient
from starlette import status

pytestmark = pytest.mark.asyncio

simple_book = {
    "name": "Test Book",
    "regular_price": 100
}

async def create_book(payload: dict, client: AsyncClient):
    response = await client.post("/book", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    return response.json()

# GET /book/id/{id}
async def test_get_book_by_id(client: AsyncClient):
    existing_book = await create_book(simple_book, client)
    response = await client.get(f"/book/id/{existing_book['id']}")
    assert response.status_code == 200
    assert response.json()["name"] == simple_book["name"]

async def test_get_book_by_fake_id(client: AsyncClient):    
    id = '123e4567-e89b-12d3-a456-426614174000'
    response = await client.get(f"/book/id/{id}")
    assert response.status_code == 404
    assert response.json() == {"detail": f"Book with id {id} not found"}
    
# GET /book/slug/{slug}
async def test_get_book_by_slug(client: AsyncClient):
    existing_book = await create_book(simple_book, client)
    response = await client.get(f"/book/slug/{existing_book['slug']}")
    assert response.status_code == 200
    assert response.json()["name"] == simple_book["name"]
    
async def test_get_book_by_fake_slug(client: AsyncClient):
    slug = 'test-book-slug'
    response = await client.get(f"/book/slug/{slug}")
    assert response.status_code == 404
    assert response.json() == {"detail": f"Book with slug {slug} not found"}

# GET /books
async def test_get_all_books(client: AsyncClient):
    await create_book(simple_book, client)
    response = await client.get("/books")
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == simple_book["name"]
    assert response.headers['x-total-count'] == '1'
    assert response.headers['x-total-pages'] == '1'
    assert response.headers['x-current-page'] == '1'
    assert response.headers['x-per-page'] == '10'
    
# GET /book/search/{q}
async def test_search_books(client: AsyncClient):
    await create_book(simple_book, client)
    q = simple_book["name"][2:6]
    response = await client.get(f"/book/search/{q}")
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == simple_book["name"]
    

# CREATE /book
async def test_create_book(client: AsyncClient):
    payload = {
        "name": "Test Book ", # with space
        "regular_price": 100
    }
    response = await client.post("/book", json=payload)
    data = response.json()
    assert response.status_code == 201
    assert data["name"] == payload["name"].strip()
    assert data['slug'] == payload["name"].strip().replace(' ', '-').lower()
    
# PATCH /book/{id}
async def test_update_book(client: AsyncClient):
    existing_book = await create_book(simple_book, client)
    payload = {
        "name": "Updated Name",
    }
    response = await client.patch(f"/book/{existing_book['id']}", json=payload)
    data = response.json()
    assert response.status_code == 200
    assert data["name"] == payload["name"]
    assert data["regular_price"] == existing_book["regular_price"]
    
# async def test_update_book_with_author_id(client: AsyncClient):
#     existing_book = await create_book(simple_book, client)
#     payload = {
#         "name": "Updated Book",
#         "author_id": "123e4567-e89b-12d3-a456-426614174000"
#     }
#     response = await client.patch(f"/book/{existing_book['id']}", json=payload)
#     data = response.json()
#     assert response.status_code == 200
#     assert data["name"] == payload["name"]
#     assert data["author_id"] == payload["author_id"]

# DELETE /book/{id}
async def test_delete_book(client: AsyncClient):
    existing_book = await create_book(simple_book, client)    
    response = await client.delete(f"/book/{existing_book['id']}")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # check if the book exists yet
    response = await client.get(f"/book/id/{existing_book['id']}")
    assert response.status_code == 404 
      
    
    
