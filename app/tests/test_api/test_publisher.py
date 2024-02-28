import pytest
from httpx import AsyncClient
from starlette import status

pytestmark = pytest.mark.asyncio

async def create_publisher(payload: dict, client: AsyncClient):
    return await client.post("/publisher", json=payload)

# GET /publisher/id/{id}
async def test_get_publisher_by_id(client: AsyncClient):
    payload = {
        "name": "Test Publisher",
        "slug": "test-publisher"
    }
    response = await create_publisher(payload, client)
    response = await client.get(f"/publisher/id/{response.json()['id']}")
    data = response.json()
    assert response.status_code == 200
    assert data["name"] == "Test Publisher"
    
# GET /publisher/slug/{slug}
async def test_get_publisher_by_slug(client: AsyncClient):
    payload = {
        "name": "Test Publisher by Slug",
        "slug": "test-publisher"
    }
    response = await create_publisher(payload, client)
    data = response.json()
    response = await client.get(f"/publisher/slug/{data['slug']}")
    data = response.json()
    assert response.status_code == 200
    assert data["name"] == "Test Publisher by Slug" 

# GET /publishers
async def test_get_all_publishers(client: AsyncClient):
    payload = {
        "name": "Test Publisher",
        "slug": "test-publisher"
    }
    await create_publisher(payload, client)
    response = await client.get("/publishers")
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Test Publisher"
    
# GET /publisher/search/{q}
# async def test_search_publishers(client: AsyncClient):
#     payload = {
#         "name": "Test Publisher",
#         "slug": "test-publisher"
#     }
#     await create_publisher(payload, client)
#     response = await client.get("/publisher/search/Test")
#     data = response.json()
#     assert len(data) == 1
#     assert data[0]["name"] == "Test Publisher"
    
#     response = await client.get("/publisher/search/Publisher")
#     data = response.json()
#     assert len(data) == 1
#     assert data[0]["name"] == "Test Publisher"
    

# POST /publisher
async def test_create_publisher(client: AsyncClient):
    payload = {
        "name": "Test Publisher",
        "slug": "test-publisher"
    }
    response = await client.post("/publisher", json=payload)
    data = response.json()
    assert response.status_code == 201
    assert data["name"] == "Test Publisher"
    # Test the slug is generated
    assert data['slug'] == 'test-publisher'
    
# PATCH /publisher/{id}
async def test_update_publisher(client: AsyncClient):
    payload = {
        "name": "Test Publisher",
        "slug": "test-publisher"
    }
    response = await create_publisher(payload, client)
    data = response.json()
    payload = {
        "name": "Updated Publisher",
    }
    response = await client.patch(f"/publisher/{data['id']}", json=payload)
    data = response.json()
    assert response.status_code == 200
    assert data["name"] == "Updated Publisher"
    assert data["slug"] == "test-publisher"

# DELETE /publisher/{id}
async def test_delete_publisher(client: AsyncClient):
    payload = {
        "name": "Test Delete Publisher",
        "slug": "test-publisher"
    }
    response = await create_publisher(payload, client)
    id = response.json()['id']
    
    response = await client.delete(f"/publisher/{id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # check if the publisher exists yet
    response = await client.get(f"/publisher/id/{id}")
    assert response.status_code == 404 
      
    
    
