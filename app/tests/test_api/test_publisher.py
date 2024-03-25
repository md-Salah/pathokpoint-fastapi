import pytest
from httpx import AsyncClient
from starlette import status

pytestmark = pytest.mark.asyncio

simple_publisher = {
    "name": "Test Publisher",
    "slug": "test-publisher",
    "description": "Test Publisher Description",
    "image": None,
    "banner": None,
    "is_islamic": True,
    "is_english": False,
    "is_popular": True,
    "country": "BD",
    "book_published": 100,
}

async def test_get_publisher_by_id(client: AsyncClient, publisher_in_db: dict):
    response = await client.get("/publisher/id/{}".format(publisher_in_db['id']))
    assert response.status_code == 200
    assert response.json().items() == publisher_in_db.items()
    

async def test_get_publisher_by_slug(client: AsyncClient, publisher_in_db: dict):
    response = await client.get("/publisher/slug/{}".format(publisher_in_db['slug']))
    assert response.status_code == 200
    assert response.json().items() == publisher_in_db.items()


@pytest.mark.parametrize("query_string_template, expected_length, modify_query_string", [
    ("", 1, lambda qs, _: qs),  
    ("?q={}", 1, lambda qs, publisher_in_db: qs.format(publisher_in_db['name'][:5])),  
    ("?name={}", 1, lambda qs, publisher_in_db: qs.format(publisher_in_db['name'])),  
    ("?slug={}", 1, lambda qs, publisher_in_db: qs.format(publisher_in_db['slug'])),  
    ("?country=BD", 1, lambda qs, _: qs), 
    ("?is_popular=true", 1, lambda qs, _: qs), 
    ("?q={}&country=BD&is_popular=true", 1, lambda qs, publisher_in_db: qs.format(publisher_in_db['name'][:5])),
])
async def test_get_all_publishers(client: AsyncClient, publisher_in_db: dict, query_string_template: str, expected_length: int, modify_query_string):
    query_string = modify_query_string(query_string_template, publisher_in_db)
    response = await client.get(f"/publisher/all{query_string}")
    assert len(response.json()) == expected_length
    assert response.json()[0].items() == publisher_in_db.items()
    assert response.headers.get("x-total-count") == "1"

    
async def test_create_publisher(client: AsyncClient):
    payload = {**simple_publisher}
    response = await client.post("/publisher", json=payload)
    assert response.status_code == 201
    assert response.json().items() >= payload.items()
    

async def test_update_publisher(client: AsyncClient, publisher_in_db: dict):
    payload = {
        "name": "Updated Publisher",
    }
    response = await client.patch("/publisher/{}".format(publisher_in_db['id']), json=payload)
    assert response.status_code == 200
    publisher_in_db.update(payload)
    publisher_in_db.pop('updated_at')
    assert response.json().items() >= publisher_in_db.items()


async def test_delete_publisher(client: AsyncClient, publisher_in_db: dict):
    response = await client.delete("/publisher/{}".format(publisher_in_db['id']))
    assert response.status_code == status.HTTP_204_NO_CONTENT
    response = await client.get("/publisher/id/{}".format(publisher_in_db['id']))
    assert response.status_code == 404 
      
    
    
