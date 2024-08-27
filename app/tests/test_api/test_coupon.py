import pytest
from httpx import AsyncClient
from starlette import status

pytestmark = pytest.mark.asyncio

simple_coupon = {
    "code": "free-delivery",
    "short_description": "Free Delivery Coupon",
    "expiry_date": "2024-12-31T00:00:00",
    "discount_type": "percentage",
    "discount_old": 15,
    "discount_new": 0,
    "min_spend_old": 499,
    "min_spend_new": 0,
}


def id_name_slug(data: dict):
    return {k: data[k] for k in ["id", "name", "slug"]}


async def test_get_coupon_by_id(client: AsyncClient, coupon_in_db: dict):
    response = await client.get(f"/coupon/id/{coupon_in_db['id']}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json().items() <= coupon_in_db.items()


async def test_get_all_coupons(client: AsyncClient, coupon_in_db: dict, admin_auth_headers: dict):
    response = await client.get("/coupon/all", headers=admin_auth_headers)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1
    assert response.json()[0].items() <= coupon_in_db.items()
    assert response.headers['x-total-count'] == '1'
    assert response.headers['x-total-pages'] == '1'
    assert response.headers['x-current-page'] == '1'
    assert response.headers['x-per-page'] == '10'


async def test_create_coupon(client: AsyncClient, admin_auth_headers: dict):
    response = await client.post("/coupon", json=simple_coupon, headers=admin_auth_headers)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json().items() >= simple_coupon.items()


async def test_create_coupon_with_relation(client: AsyncClient, author_in_db: dict, publisher_in_db: dict, category_in_db: dict, admin_auth_headers: dict):
    payload = {
        **simple_coupon,
        "include_authors": [author_in_db['id']],
        "include_publishers": [publisher_in_db["id"]],
        "include_categories": [category_in_db['id']],
        "exclude_categories": [category_in_db['id']]
    }
    response = await client.post("/coupon", json=payload, headers=admin_auth_headers)
    assert response.status_code == status.HTTP_201_CREATED
    payload["include_authors"] = [id_name_slug(author_in_db)]
    payload["include_publishers"] = [id_name_slug(publisher_in_db)]
    payload["include_categories"] = [id_name_slug(category_in_db)]
    payload["exclude_categories"] = [id_name_slug(category_in_db)]
    assert response.json().items() >= payload.items()


async def test_update_coupon(client: AsyncClient, coupon_in_db: dict, admin_auth_headers: dict):
    payload = {
        **coupon_in_db,
        "expiry_date": "2048-12-31T00:00:00",
    }
    response = await client.patch(f"/coupon/{coupon_in_db['id']}", json=payload, headers=admin_auth_headers)
    assert response.status_code == status.HTTP_200_OK
    payload.pop('updated_at')
    assert payload.items() <= response.json().items()


async def test_update_coupon_with_relation(client: AsyncClient, author_in_db: dict, category_in_db: dict, admin_auth_headers: dict):
    payload = {
        **simple_coupon,
        "include_authors": [author_in_db['id']],
        "include_categories": [category_in_db['id']],
    }
    response = await client.post("/coupon", json=payload, headers=admin_auth_headers)
    assert response.status_code == status.HTTP_201_CREATED

    payload.update({
        'include_categories': []
    })
    response = await client.patch(f"/coupon/{response.json()['id']}", json=payload, headers=admin_auth_headers)
    assert response.status_code == status.HTTP_200_OK
    payload["include_authors"] = [id_name_slug(author_in_db)]
    assert response.json().items() >= payload.items()


async def test_delete_coupon(client: AsyncClient, coupon_in_db: dict, admin_auth_headers: dict):
    response = await client.delete(f"/coupon/{coupon_in_db['id']}", headers=admin_auth_headers)
    assert response.status_code == status.HTTP_204_NO_CONTENT
