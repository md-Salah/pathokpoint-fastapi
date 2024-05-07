import pytest
from httpx import AsyncClient
from starlette import status
from unittest.mock import patch

pytestmark = pytest.mark.asyncio

simple_review = {
    "comment": "Great book i have ever read!",
    "delivery_rating": 5,
    "product_rating": 5,
    "time_rating": 5,
    "website_rating": 5
}


@pytest.fixture
def mock_delete_file():
    with patch("app.controller.review.image_service.delete_file_from_cloudinary") as mock_delete_file:
        yield mock_delete_file


async def test_get_review_by_id(client: AsyncClient, review_in_db: dict):
    response = await client.get(f"/review/id/{review_in_db['id']}")
    assert response.status_code == status.HTTP_200_OK
    review_in_db.pop('access_token')
    assert response.json().items() >= review_in_db.items()


async def test_get_all_reviews(client: AsyncClient, review_in_db: dict):
    response = await client.get("/review/all")
    assert len(response.json()) == 1
    review_in_db.pop('access_token')
    assert response.json()[0].items() >= review_in_db.items()


async def test_create_book_review(client: AsyncClient, book_in_db: dict, user_in_db: dict):
    payload = {
        **simple_review,
        "book_id": book_in_db['id'],
    }
    response = await client.post("/review/new", json=payload)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    response = await client.post("/review/new", json=payload, headers={"Authorization": "Bearer {}".format(user_in_db['token']['access_token'])})
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json().items() >= payload.items()


async def test_create_order_review(client: AsyncClient, book_in_db: dict, user_in_db: dict):
    headers = {"Authorization": f"Bearer {
        user_in_db['token']['access_token']}"}
    response = await client.post('/order/new', json={
        "order_items": [
            {
                "book_id": book_in_db['id'],
                "quantity": 1,
            }
        ]
    }, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED
    order_in_db = response.json()

    payload = {
        **simple_review,
        "order_id": order_in_db['id'],
    }
    response = await client.post("/review/new", json=payload, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json().items() >= payload.items()


async def test_update_review(client: AsyncClient, review_in_db: dict):
    payload = {
        'comment': 'I have found this book helpful'
    }
    response = await client.patch(f"/review/{review_in_db['id']}", json=payload, headers={"Authorization": f"Bearer {review_in_db['access_token']}"})
    assert response.status_code == status.HTTP_200_OK
    review_in_db.pop('access_token')
    review_in_db.update(payload)
    review_in_db.pop('updated_at')
    assert response.json().items() >= review_in_db.items()


async def test_update_review_image(mock_delete_file, client: AsyncClient, review_in_db: dict):
    mock_delete_file.return_value = True
    payload = {
        'images': []
    }
    response = await client.patch(f"/review/{review_in_db['id']}", json=payload, headers={"Authorization": f"Bearer {review_in_db['access_token']}"})
    assert response.status_code == status.HTTP_200_OK
    review_in_db.pop('access_token')
    review_in_db.update(payload)
    review_in_db.pop('updated_at')
    assert response.json().items() >= review_in_db.items()


async def test_approve_review(client: AsyncClient, review_in_db: dict, admin_access_token: str):
    response = await client.patch(f"/review/approve/{review_in_db['id']}",
                                  headers={"Authorization": f"Bearer {admin_access_token}"})
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['is_approved'] is True


async def test_delete_review(mock_delete_file, client: AsyncClient, review_in_db: dict):
    mock_delete_file.return_value = True
    response = await client.delete(f"/review/{review_in_db['id']}",
                                   headers={"Authorization": f"Bearer {review_in_db['access_token']}"})
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Image should be deleted
    response = await client.get(f'/image/id/{review_in_db["images"][0]["id"]}')
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_delete_review_by_admin(mock_delete_file, client: AsyncClient, review_in_db: dict, admin_access_token: str):
    mock_delete_file.return_value = True
    response = await client.delete(f"/review/{review_in_db['id']}",
                                   headers={"Authorization": f"Bearer {admin_access_token}"})
    assert response.status_code == status.HTTP_204_NO_CONTENT
