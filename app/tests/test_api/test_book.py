import pytest
from httpx import AsyncClient
from unittest.mock import MagicMock
from starlette import status
from typing import Any, Callable

pytestmark = pytest.mark.asyncio

simple_book = {
    "sku": "99-5432",
    "name": "Test Book",
    "slug": "test-book",
    "regular_price": 100,
    "sale_price": 90,
    "manage_stock": True,
    "quantity": 10,
    "is_used": True,
    "condition": "old-like-new",
    "is_popular": True,
}


async def test_get_book_by_id(client: AsyncClient, book_in_db: dict):
    response = await client.get(f"/book/id/{book_in_db['id']}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json().items() <= book_in_db.items()


async def test_get_book_by_public_id(client: AsyncClient, book_in_db: dict):
    response = await client.get(f"/book/public_id/{book_in_db['public_id']}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json().items() <= book_in_db.items()


@pytest.mark.parametrize("query_string_template, expected_length, modify_query_string", [
    ("", 1, lambda qs, book_in_db: qs),
    ("?q={}", 1, lambda qs, book_in_db: qs.format(
        book_in_db['name'][:5])),  # type: ignore
    ("?name={}", 1, lambda qs, book_in_db: qs.format(
        book_in_db['name'])),  # type: ignore
    ("?slug={}", 1, lambda qs, book_in_db: qs.format(
        book_in_db['slug'])),  # type: ignore
    ("?country=BD", 1, lambda qs, book_in_db: qs),
    ("?is_popular=true", 1, lambda qs, book_in_db: qs),
    ("?q={}&country=BD&is_popular=true", 1,
     lambda qs, bdb: qs.format(bdb['name'][:5])),  # type: ignore
])
async def test_get_all_books(client: AsyncClient, book_in_db: dict[str, Any], query_string_template: str, expected_length: int, modify_query_string):
    query_string = modify_query_string(query_string_template, book_in_db)
    response = await client.get(f"/book/all{query_string}")
    assert len(response.json()) == expected_length
    assert response.json()[0].items() <= book_in_db.items()
    assert response.headers.get("x-total-count") == str(expected_length)


# async def test_get_all_books_minimal(client: AsyncClient, book_in_db: dict):
#     response = await client.get("/book/all-minimal")
#     assert len(response.json()) == 1
#     assert response.json()[0].items() <= book_in_db.items()
#     assert response.headers.get("x-total-count") == '1'


async def test_create_book(client: AsyncClient, author_in_db: dict, category_in_db: dict, publisher_in_db: dict, admin_auth_headers: dict):
    payload = {
        **simple_book,
        "authors": [author_in_db['id']],
        "categories": [category_in_db['id']],
        "publisher_id": publisher_in_db["id"]
    }
    response = await client.post("/book", json=payload, headers=admin_auth_headers)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json().items() >= simple_book.items()

    def id_name_slug(data: dict):
        return {k: data[k] for k in ["id", "name", "slug"]}
    assert response.json()["authors"] == [id_name_slug(author_in_db)]
    assert response.json()["categories"] == [id_name_slug(category_in_db)]
    assert response.json()["publisher"] == id_name_slug(publisher_in_db)


async def test_create_book_bulk(client: AsyncClient, author_in_db: dict, category_in_db: dict, publisher_in_db: dict, admin_auth_headers: dict):
    payload = [
        {
            **simple_book,
            "authors": [author_in_db['id']],
            "categories": [category_in_db['id']],
            "publisher_id": publisher_in_db["id"]
        }
    ]
    response = await client.post("/book/bulk", json=payload, headers=admin_auth_headers)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()[0].items() >= simple_book.items()


async def test_update_book(client: AsyncClient, book_in_db: dict, admin_auth_headers: dict):
    payload = {
        **book_in_db,
        "name": "Updated Name",
        "quantity": 20,
    }
    response = await client.patch(f"/book/{book_in_db['id']}", json=payload, headers=admin_auth_headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name"] == payload["name"]
    payload.pop('updated_at')
    assert payload.items() <= response.json().items()


async def test_upload_book_images(client: AsyncClient, book_in_db: dict, admin_auth_headers: dict, 
                                  img_uploader: Callable, mock_upload_file: MagicMock, mock_delete_file: MagicMock):
    await img_uploader("/image/admin?book_id={}".format(book_in_db['id']), admin_auth_headers, mock_upload_file)
    res = await client.get(f"/book/id/{book_in_db['id']}")
    assert res.status_code == status.HTTP_200_OK
    assert len(res.json()['images']) == 1

    # Test image deletion on book deletion
    response = await client.delete(f"/book/{book_in_db['id']}", headers=admin_auth_headers)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    mock_delete_file.assert_called_once()


async def test_delete_book(client: AsyncClient, book_in_db: dict, admin_auth_headers: dict):
    response = await client.delete(f"/book/{book_in_db['id']}", headers=admin_auth_headers)
    assert response.status_code == status.HTTP_204_NO_CONTENT


async def test_delete_book_bulk(client: AsyncClient, book_in_db: dict, admin_auth_headers: dict):
    response = await client.delete(f"/book/bulk/{book_in_db['id']}", headers=admin_auth_headers)
    assert response.status_code == status.HTTP_204_NO_CONTENT
