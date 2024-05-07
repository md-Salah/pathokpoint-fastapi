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
    "image_id": None,
    "banner_id": None,
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


async def test_create_author(client: AsyncClient, image_in_db: dict, admin_auth_headers: dict):
    payload = {
        **simple_author,
        "image_id": image_in_db['id'],
        'banner_id': image_in_db['id']
    }
    response = await client.post("/author", json=payload, headers=admin_auth_headers)
    assert response.status_code == 201
    payload.update({'image': image_in_db, 'banner': image_in_db})
    assert response.json().items() >= payload.items()


async def test_update_author(client: AsyncClient, author_in_db: dict, image_in_db: dict, admin_auth_headers: dict):
    payload = {
        "name": "Updated Author",
        "image_id": image_in_db['id'],
    }
    response = await client.patch(f"/author/{author_in_db['id']}", json=payload, headers=admin_auth_headers)
    assert response.status_code == 200
    author_in_db.update(payload)
    author_in_db.pop('updated_at')
    author_in_db.update({'image': image_in_db})
    assert response.json().items() >= author_in_db.items()


async def test_delete_author(client: AsyncClient, author_in_db: dict, admin_auth_headers: dict):
    response = await client.delete(f"/author/{author_in_db['id']}", headers=admin_auth_headers)
    assert response.status_code == status.HTTP_204_NO_CONTENT


async def test_follow_author(client: AsyncClient, author_in_db: dict, user_in_db: dict):
    headers = {'Authorization': 'Bearer {}'.format(
        user_in_db["token"]["access_token"])}
    response = await client.post('/author/follow/{}'.format(author_in_db['id']), headers=headers)
    assert response.status_code == 200
    assert response.json()['followers_count'] == 1


async def test_unfollow_author(client: AsyncClient, author_in_db: dict, user_in_db: dict):
    headers = {'Authorization': 'Bearer {}'.format(
        user_in_db["token"]["access_token"])}

    # Follow
    response = await client.post('/author/follow/{}'.format(author_in_db['id']), headers=headers)
    assert response.status_code == 200
    assert response.json()['followers_count'] == 1

    # Unfollow
    response = await client.post('/author/unfollow/{}'.format(author_in_db['id']), headers=headers)
    assert response.status_code == 200
    assert response.json()['followers_count'] == 0
