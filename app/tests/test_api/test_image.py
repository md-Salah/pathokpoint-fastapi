import pytest
from httpx import AsyncClient
from starlette import status
from unittest.mock import patch

pytestmark = pytest.mark.asyncio

async def test_get_image_by_id(client: AsyncClient, image_in_db: dict):
    response = await client.get(f"/image/id/{image_in_db['id']}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json().items() >= image_in_db.items()


async def test_get_all_images(client: AsyncClient, image_in_db: dict):
    response = await client.get("/images")
    assert len(response.json()) == 1
    assert response.json()[0].items() >= image_in_db.items()

@patch("app.controller.image.upload_file_to_cloudinary")
async def test_create_image(upload_file, client: AsyncClient):
    upload_file.return_value = 'https://res.cloudinary.com/dummy/image/upload/v1629780000/test.jpg'

    with open("dummy/test.jpg", "rb") as f:
        response = await client.post("/image",
                                     files={"file": ("image.jpg", f, "image/jpeg")}, data={'alt': 'test-image'})

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json().items() >= {
        'name': 'image.jpg', 'alt': 'test-image'}.items()
    assert response.json()['src'] is not None
    upload_file.assert_called_once()

@patch("app.controller.image.delete_file_from_cloudinary")
async def test_delete_image(delete_file, client: AsyncClient, image_in_db: dict):
    delete_file.return_value = True
    response = await client.delete("/image/{}".format(image_in_db['id']))
    assert response.status_code == status.HTTP_204_NO_CONTENT
