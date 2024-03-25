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


@pytest_asyncio.fixture(name="tag_in_db")
async def create_tag(client: AsyncClient):
    response = await client.post("/tag", json=simple_tag)
    assert response.status_code == status.HTTP_201_CREATED
    return response.json()


async def test_get_tag_by_id(client: AsyncClient, tag_in_db: dict):
    response = await client.get(f"/tag/id/{tag_in_db['id']}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json().items() >= tag_in_db.items()


async def test_get_all_tags(client: AsyncClient, tag_in_db: dict):
    response = await client.get("/tag/all")
    assert len(response.json()) == 1
    assert response.json()[0].items() >= tag_in_db.items()


async def test_create_tag(client: AsyncClient):
    response = await client.post("/tag", json=simple_tag)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json().items() >= simple_tag.items()


async def test_update_tag(client: AsyncClient, tag_in_db: dict):
    tag_in_db['name'] = 'tag2'
    tag_in_db.pop('updated_at')
    response = await client.patch(f"/tag/{tag_in_db['id']}", json=tag_in_db)
    assert response.status_code == status.HTTP_200_OK
    assert response.json().items() >= tag_in_db.items()


async def test_delete_tag(client: AsyncClient, tag_in_db: dict):
    response = await client.delete("/tag/{}".format(tag_in_db['id']))
    assert response.status_code == status.HTTP_204_NO_CONTENT
