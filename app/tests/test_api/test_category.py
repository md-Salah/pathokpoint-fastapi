import pytest
from httpx import AsyncClient
from starlette import status

pytestmark = pytest.mark.asyncio

simple_category = {
    "name": "Fiction",
    "slug": "fiction",
    "description": "This is a fiction category",
    "is_islamic": False,
    "is_english_featured": True,
    "is_bangla_featured": False,
    "is_job_featured": False,
    "is_comics": True,
    "is_popular": True,
    "is_big_sale": False,
}


async def test_get_category_by_id(client: AsyncClient, category_in_db: dict):
    response = await client.get("/category/id/{}".format(category_in_db['id']))
    assert response.status_code == 200
    assert response.json().items() == category_in_db.items()


async def test_get_category_by_slug(client: AsyncClient, category_in_db: dict):
    response = await client.get("/category/slug/{}".format(category_in_db['slug']))
    assert response.status_code == 200
    assert response.json().items() == category_in_db.items()


@pytest.mark.parametrize("query_string_template, expected_length, modify_query_string", [
    ("", 1, lambda qs, _: qs),
    ("?q={}", 1, lambda qs, category_in_db: qs.format(
        category_in_db['name'][:5])),
    ("?name={}", 1, lambda qs, category_in_db: qs.format(
        category_in_db['name'])),
    ("?slug={}", 1, lambda qs, category_in_db: qs.format(
        category_in_db['slug'])),
    ("?is_popular=true", 1, lambda qs, _: qs),
    ("?q={}&is_popular=true", 1, lambda qs,
     category_in_db: qs.format(category_in_db['name'][:5])),
])
async def test_get_all_categories(client: AsyncClient, category_in_db: dict, query_string_template: str, expected_length: int, modify_query_string):
    query_string = modify_query_string(query_string_template, category_in_db)
    response = await client.get(f"/category/all{query_string}")
    assert len(response.json()) == expected_length
    assert response.json()[0].items() == category_in_db.items()
    assert response.headers.get("x-total-count") == "1"


async def test_create_category(client: AsyncClient, image_in_db: dict):
    payload = {
        **simple_category,
        'image': image_in_db['id'],
        'banner': image_in_db['id'],
    }
    response = await client.post("/category", json=payload)
    assert response.status_code == 201
    payload['image'] = image_in_db
    payload['banner'] = image_in_db
    assert response.json().items() >= payload.items()


async def test_update_category(client: AsyncClient, category_in_db: dict):
    payload = {
        "name": "Updated Category",
    }
    response = await client.patch("/category/{}".format(category_in_db['id']), json=payload)
    assert response.status_code == 200
    category_in_db.update(payload)
    category_in_db.pop('updated_at')
    assert response.json().items() >= category_in_db.items()


async def test_delete_category(client: AsyncClient, category_in_db: dict):
    response = await client.delete("/category/{}".format(category_in_db['id']))
    assert response.status_code == status.HTTP_204_NO_CONTENT
