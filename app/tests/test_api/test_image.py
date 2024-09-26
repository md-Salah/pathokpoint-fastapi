import pytest
from httpx import AsyncClient
from starlette import status
from unittest.mock import MagicMock

pytestmark = pytest.mark.asyncio


async def test_get_image_by_id(client: AsyncClient, mock_signed_url: MagicMock, image_in_db: dict, admin_auth_headers: dict):
    response = await client.get(f"/image/id/{image_in_db['id']}", headers=admin_auth_headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json().items() >= image_in_db.items()
    mock_signed_url.assert_called_once()


async def test_get_all_images(client: AsyncClient, image_in_db: dict, admin_auth_headers: dict):
    response = await client.get("/image/all", headers=admin_auth_headers)
    assert len(response.json()) == 1
    assert response.json()[0].items() >= image_in_db.items()


async def test_create_image(mock_upload_file: MagicMock, client: AsyncClient, author_in_db: dict, admin_auth_headers: dict):
    mock_upload_file.return_value = 'key'

    with open("dummy/test.jpg", "rb") as f:
        response = await client.post("/image/admin?author_id={}".format(author_in_db['id']),
                                     files=[
                                         ("files", ("image.jpg", f, "image/jpeg"))
        ],
            headers=admin_auth_headers)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()[0].items() >= {'name': 'image.jpg'}.items()
    assert response.json()[0]['src'] is not None
    assert response.json()[0]['public_id'] is not None
    mock_upload_file.assert_called_once()
