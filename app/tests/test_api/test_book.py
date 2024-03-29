import pytest
import pytest_asyncio
from httpx import AsyncClient
from starlette import status

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


@pytest_asyncio.fixture(name="book_in_db")
async def create_book(client: AsyncClient):
    response = await client.post("/book", json=simple_book)
    assert response.status_code == status.HTTP_201_CREATED
    return response.json()


async def test_get_book_by_id(client: AsyncClient, book_in_db: dict):
    response = await client.get(f"/book/id/{book_in_db['id']}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json().items() <= book_in_db.items()


@pytest.mark.parametrize("query_string_template, expected_length, modify_query_string", [
    ("", 1, lambda qs, book_in_db: qs),
    ("?q={}", 1, lambda qs, book_in_db: qs.format(book_in_db['name'][:5])),
    ("?name={}", 1, lambda qs, book_in_db: qs.format(book_in_db['name'])),
    ("?slug={}", 1, lambda qs, book_in_db: qs.format(book_in_db['slug'])),
    ("?country=BD", 1, lambda qs, book_in_db: qs),
    ("?is_popular=true", 1, lambda qs, book_in_db: qs),
    ("?q={}&country=BD&is_popular=true", 1,
     lambda qs, bdb: qs.format(bdb['name'][:5])),
])
async def test_get_all_books(client: AsyncClient, book_in_db: dict, query_string_template: str, expected_length: int, modify_query_string):
    query_string = modify_query_string(query_string_template, book_in_db)
    response = await client.get(f"/book/all{query_string}")
    assert len(response.json()) == expected_length
    assert response.json()[0].items() <= book_in_db.items()
    assert response.headers.get("x-total-count") == str(expected_length)


async def test_create_book(client: AsyncClient, author_in_db: dict, category_in_db: dict, publisher_in_db: dict):
    payload = {
        **simple_book,
        "authors": [author_in_db['id']],
        "categories": [category_in_db['id']],
        "publisher": publisher_in_db["id"]
    }    
    response = await client.post("/book", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json().items() >= simple_book.items()

    def id_name_slug(data: dict):
        return {k: data[k] for k in ["id", "name", "slug"]}
    assert response.json()["authors"] == [id_name_slug(author_in_db)]
    assert response.json()["categories"] == [id_name_slug(category_in_db)]
    assert response.json()["publisher"] == id_name_slug(publisher_in_db)


async def test_update_book(client: AsyncClient, book_in_db: dict):
    payload = {
        **book_in_db,
        "name": "Updated Name",
        "quantity": 20,
    }
    response = await client.patch(f"/book/{book_in_db['id']}", json=payload)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name"] == payload["name"]
    payload.pop('updated_at')
    assert payload.items() <= response.json().items()


async def test_delete_book(client: AsyncClient, book_in_db: dict):
    response = await client.delete(f"/book/{book_in_db['id']}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    response = await client.get(f"/book/id/{book_in_db['id']}")
    assert response.status_code == 404
