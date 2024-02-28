import pytest
from httpx import AsyncClient
from starlette import status

pytestmark = pytest.mark.asyncio

async def create_author(payload: dict, client: AsyncClient):
    return await client.post("/author", json=payload)

# GET /author/id/{id}
async def test_get_author_by_id(client: AsyncClient):
    payload = {
        "name": "Test Author",
        "slug": "test-author"
    }
    response = await create_author(payload, client)
    response = await client.get(f"/author/id/{response.json()['id']}")
    data = response.json()
    assert response.status_code == 200
    assert data["name"] == "Test Author"
    
# GET /author/slug/{slug}
async def test_get_author_by_slug(client: AsyncClient):
    payload = {
        "name": "Test Author by Slug",
        "slug": "test-author"
    }
    response = await create_author(payload, client)
    data = response.json()
    response = await client.get(f"/author/slug/{data['slug']}")
    data = response.json()
    assert response.status_code == 200
    assert data["name"] == "Test Author by Slug" 

# GET /authors
async def test_get_all_authors(client: AsyncClient):
    payload = {
        "name": "Test Author",
        "slug": "test-author"
    }
    await create_author(payload, client)
    response = await client.get("/authors")
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Test Author"
    
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
    payload = {
        "name": "Test Author",
        "slug": "test-author"
    }
    response = await client.post("/author", json=payload)
    data = response.json()
    assert response.status_code == 201
    assert data["name"] == "Test Author"
    # Test the slug is generated
    assert data['slug'] == 'test-author'
    
# PATCH /author/{id}
async def test_update_author(client: AsyncClient):
    payload = {
        "name": "Test Author",
        "slug": "test-author"
    }
    response = await create_author(payload, client)
    data = response.json()
    payload = {
        "name": "Updated Author",
    }
    response = await client.patch(f"/author/{data['id']}", json=payload)
    data = response.json()
    assert response.status_code == 200
    assert data["name"] == "Updated Author"
    assert data["slug"] == "test-author"

# DELETE /author/{id}
async def test_delete_author(client: AsyncClient):
    payload = {
        "name": "Test Delete Author",
        "slug": "test-author"
    }
    response = await create_author(payload, client)
    id = response.json()['id']
    
    response = await client.delete(f"/author/{id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # check if the author exists yet
    response = await client.get(f"/author/id/{id}")
    assert response.status_code == 404 
      
    
    
