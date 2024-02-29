import pytest
from httpx import AsyncClient
from starlette import status

pytestmark = pytest.mark.asyncio

simple_author = {
        "name": "Test Author",
        "slug": "test-author"
    }

async def create_author(payload: dict, client: AsyncClient):
    response = await client.post("/author", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    return response.json()

# GET /author/id/{id}
async def test_get_author_by_id(client: AsyncClient):
    existing_author = await create_author(simple_author, client)
    response = await client.get(f"/author/id/{existing_author['id']}")
    assert response.status_code == 200
    assert response.json()["name"] == simple_author["name"]
    
# GET /author/slug/{slug}
async def test_get_author_by_slug(client: AsyncClient):
    existing_author = await create_author(simple_author, client)
    response = await client.get(f"/author/slug/{existing_author['slug']}")
    assert response.status_code == 200
    assert response.json()["name"] == simple_author["name"] 

# GET /authors
async def test_get_all_authors(client: AsyncClient):
    await create_author(simple_author, client)
    response = await client.get("/authors")
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == simple_author["name"]
    
# GET /author/search/{q}
# async def test_search_authors(client: AsyncClient):
#     payload = {
#         "name": "Test Author",
#         "slug": "test-author"
#     }
#     await create_author(payload, client)
#     response = await client.get("/author/search/Test")
#     data = response.json()
#     assert len(data) == 1
#     assert data[0]["name"] == "Test Author"
    
#     response = await client.get("/author/search/Author")
#     data = response.json()
#     assert len(data) == 1
#     assert data[0]["name"] == "Test Author"
    

# POST /author
async def test_create_author(client: AsyncClient):
    response = await client.post("/author", json=simple_author)
    data = response.json()
    assert response.status_code == 201
    assert data["name"] == simple_author["name"]
    assert data['slug'] == simple_author['slug']
    
# PATCH /author/{id}
async def test_update_author(client: AsyncClient):
    existing_author = await create_author(simple_author, client)
    payload = {
        "name": "Updated Author",
    }
    response = await client.patch(f"/author/{existing_author['id']}", json=payload)
    data = response.json()
    assert response.status_code == 200
    assert data["name"] == payload["name"]
    assert data["slug"] == simple_author["slug"]

# DELETE /author/{id}
async def test_delete_author(client: AsyncClient):
    existing_author = await create_author(simple_author, client)
    id = existing_author['id']
    
    response = await client.delete(f"/author/{id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # check if the author exists yet
    response = await client.get(f"/author/id/{id}")
    assert response.status_code == 404 
      
    
    
