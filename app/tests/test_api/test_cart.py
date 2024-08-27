import pytest
from httpx import AsyncClient
from starlette import status

pytestmark = pytest.mark.asyncio


async def test_get_suggested_coupons(client: AsyncClient, coupon_in_db: dict):
    response = await client.get("/cart/suggested-coupons")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1
    assert response.json()[0].items() <= coupon_in_db.items()


async def test_apply_coupon(client: AsyncClient, book_in_db: dict, coupon_in_db: dict):
    response = await client.post("/cart/apply-coupon", json={
        'coupon_code': coupon_in_db["code"],
        'order_items': [
            {
                "book_id": book_in_db["id"],
                "quantity": 2
            }
        ]
    }, headers={"Authorization": "Bearer fake-token"})
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['discount'] == book_in_db['sale_price'] * \
        2 * coupon_in_db['discount_old'] / 100


async def test_verify_stock(client: AsyncClient, book_in_db: dict):
    response = await client.post("/cart/verify-stock", json={
        'order_items': [
            {
                "book_id": book_in_db["id"],
                "quantity": 2
            }
        ]
    })
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "ok"}