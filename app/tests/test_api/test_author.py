import pytest
from httpx import AsyncClient
from starlette import status

pytestmark = pytest.mark.asyncio

simple_author = {
    "birth_date": "1948-11-13",
    "book_published": 200,
    "city": "dhaka",
    "country": "BD",
    "death_date": "2012-07-19",
    "description": "বাংলাদেশের প্রখ্যাত লেখক",
    "is_popular": True,
    "name": "হুমায়ূন আহমেদ",
    "slug": "humayun-ahmed",
    "image": None,
    "banner": None,
}


async def test_get_author_by_id(client: AsyncClient, author_in_db: dict):
    response = await client.get(f"/author/id/{author_in_db['id']}")
    assert response.status_code == 200
    assert response.json().items() == author_in_db.items()


async def test_get_author_by_slug(client: AsyncClient, author_in_db: dict):
    response = await client.get(f"/author/slug/{author_in_db['slug']}")
    assert response.status_code == 200
    assert response.json().items() == author_in_db.items()


@pytest.mark.parametrize("query_string_template, expected_length, modify_query_string", [
    ("", 1, lambda qs, _: qs),
    ("?q={}", 1, lambda qs, author_in_db: qs.format(author_in_db['name'][:5])),
    ("?name={}", 1, lambda qs, author_in_db: qs.format(author_in_db['name'])),
    ("?slug={}", 1, lambda qs, author_in_db: qs.format(author_in_db['slug'])),
    ("?country=BD", 1, lambda qs, _: qs),
    ("?is_popular=true", 1, lambda qs, _: qs),
    ("?q={}&country=BD&is_popular=true", 1, lambda qs,
     author_in_db: qs.format(author_in_db['name'][:5])),
])
async def test_get_all_authors(client: AsyncClient, author_in_db: dict, query_string_template: str, expected_length: int, modify_query_string):
    query_string = modify_query_string(query_string_template, author_in_db)
    response = await client.get(f"/author/all{query_string}")
    assert len(response.json()) == expected_length
    assert response.json()[0].items() == author_in_db.items()
    assert response.headers.get("x-total-count") == "1"


async def test_create_author(client: AsyncClient, image_in_db: dict):
    payload = {
        **simple_author,
        "image": image_in_db['id'],
        'banner': image_in_db['id']
    }
    response = await client.post("/author", json=payload)
    assert response.status_code == 201
    payload['image'] = image_in_db
    payload['banner'] = image_in_db
    assert response.json().items() >= payload.items()


async def test_update_author(client: AsyncClient, author_in_db: dict):
    payload = {
        "name": "Updated Author",
    }
    response = await client.patch(f"/author/{author_in_db['id']}", json=payload)
    assert response.status_code == 200
    author_in_db.update(payload)
    author_in_db.pop('updated_at')
    assert response.json().items() >= author_in_db.items()


async def test_delete_author(client: AsyncClient, author_in_db: dict):
    response = await client.delete(f"/author/{author_in_db['id']}")
    assert response.status_code == status.HTTP_204_NO_CONTENT
