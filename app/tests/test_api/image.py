import pytest
import pytest_asyncio
from httpx import AsyncClient
from starlette import status

pytestmark = pytest.mark.asyncio


@pytest_asyncio.fixture(name="image_in_db")
async def create_image(client: AsyncClient):
    with open("dummy/test.jpg", "rb") as f:
        response = await client.post("/image",
                                     files={"file": ("image.jpg", f, "image/jpeg")}, data={'alt': 'test-image'})
    assert response.status_code == status.HTTP_201_CREATED
    return response.json()


async def test_get_image_by_id(client: AsyncClient, image_in_db: dict):
    response = await client.get(f"/image/id/{image_in_db['id']}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json().items() >= image_in_db.items()


async def test_get_all_images(client: AsyncClient, image_in_db: dict):
    response = await client.get("/images")
    assert len(response.json()) == 1
    assert response.json()[0].items() >= image_in_db.items()


async def test_create_image(client: AsyncClient):

    with open("dummy/test.jpg", "rb") as f:
        response = await client.post("/image",
                                     files={"file": ("image.jpg", f, "image/jpeg")}, data={'alt': 'test-image'})

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json().items() >= {
        'name': 'image.jpg', 'alt': 'test-image'}.items()
    assert response.json()['src'] is not None


async def test_delete_image(client: AsyncClient, image_in_db: dict):
    id = image_in_db['id']
    response = await client.delete(f"/image/{id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    response = await client.get(f"/image/id/{id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND
