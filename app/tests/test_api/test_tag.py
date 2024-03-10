import pytest
import pytest_asyncio
from httpx import AsyncClient
from starlette import status

pytestmark = pytest.mark.asyncio

simple_tag = {
        "name": "tag1",
        "slug": "tag1",
        "private": False
    }

@pytest_asyncio.fixture(name="created_tag")
async def create_tag(client: AsyncClient):
    response = await client.post("/tag", json=simple_tag)
    assert response.status_code == status.HTTP_201_CREATED
    return response.json()

# GET /tag/id/{id}
async def test_get_tag_by_id(client: AsyncClient, created_tag: dict):
    response = await client.get(f"/tag/id/{created_tag['id']}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json().items() >= created_tag.items()

# GET /tags
async def test_get_all_tags(client: AsyncClient, created_tag: dict):
    response = await client.get("/tags")
    assert len(response.json()) == 1
    assert response.json()[0].items() >= created_tag.items()
    
# POST /tag
async def test_create_tag(client: AsyncClient):
    response = await client.post("/tag", json=simple_tag)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json().items() >= simple_tag.items()

    
# PATCH /tag/{id}
async def test_update_tag(client: AsyncClient, created_tag: dict):
    created_tag['name'] = 'tag2'
    created_tag.pop('updated_at')
    response = await client.patch(f"/tag/{created_tag['id']}", json=created_tag)
    assert response.status_code == status.HTTP_200_OK
    assert response.json().items() >= created_tag.items()

# DELETE /tag/{id}
async def test_delete_tag(client: AsyncClient, created_tag: dict):
    id = created_tag['id']
    response = await client.delete(f"/tag/{id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    response = await client.get(f"/tag/id/{id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND
      
    
    
