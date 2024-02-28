import pytest
from httpx import AsyncClient
from starlette import status

pytestmark = pytest.mark.asyncio

async def create_category(payload: dict, client: AsyncClient):
    return await client.post("/category", json=payload)

# GET /category/id/{id}
async def test_get_category_by_id(client: AsyncClient):
    payload = {
        "name": "Test Category",
        "slug": "test-category"
    }
    response = await create_category(payload, client)
    response = await client.get(f"/category/id/{response.json()['id']}")
    data = response.json()
    assert response.status_code == 200
    assert data["name"] == "Test Category"
    
# GET /category/slug/{slug}
async def test_get_category_by_slug(client: AsyncClient):
    payload = {
        "name": "Test Category by Slug",
        "slug": "test-category"
    }
    response = await create_category(payload, client)
    data = response.json()
    response = await client.get(f"/category/slug/{data['slug']}")
    data = response.json()
    assert response.status_code == 200
    assert data["name"] == "Test Category by Slug" 

# GET /categorys
async def test_get_all_categorys(client: AsyncClient):
    payload = {
        "name": "Test Category",
        "slug": "test-category"
    }
    await create_category(payload, client)
    response = await client.get("/categorys")
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Test Category"
    
# GET /category/search/{q}
# async def test_search_categorys(client: AsyncClient):
#     payload = {
#         "name": "Test Category",
#         "slug": "test-category"
#     }
#     await create_category(payload, client)
#     response = await client.get("/category/search/Test")
#     data = response.json()
#     assert len(data) == 1
#     assert data[0]["name"] == "Test Category"
    
#     response = await client.get("/category/search/Category")
#     data = response.json()
#     assert len(data) == 1
#     assert data[0]["name"] == "Test Category"
    

# POST /category
async def test_create_category(client: AsyncClient):
    payload = {
        "name": "Test Category",
        "slug": "test-category"
    }
    response = await client.post("/category", json=payload)
    data = response.json()
    assert response.status_code == 201
    assert data["name"] == "Test Category"
    # Test the slug is generated
    assert data['slug'] == 'test-category'
    
# PATCH /category/{id}
async def test_update_category(client: AsyncClient):
    payload = {
        "name": "Test Category",
        "slug": "test-category"
    }
    response = await create_category(payload, client)
    data = response.json()
    payload = {
        "name": "Updated Category",
    }
    response = await client.patch(f"/category/{data['id']}", json=payload)
    data = response.json()
    assert response.status_code == 200
    assert data["name"] == "Updated Category"
    assert data["slug"] == "test-category"

# DELETE /category/{id}
async def test_delete_category(client: AsyncClient):
    payload = {
        "name": "Test Delete Category",
        "slug": "test-category"
    }
    response = await create_category(payload, client)
    id = response.json()['id']
    
    response = await client.delete(f"/category/{id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # check if the category exists yet
    response = await client.get(f"/category/id/{id}")
    assert response.status_code == 404 
      
    
    
