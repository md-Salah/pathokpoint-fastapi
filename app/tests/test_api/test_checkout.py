import pytest
from httpx import AsyncClient
from starlette import status

pytestmark = pytest.mark.asyncio


async def test_get_checkout_summary(client: AsyncClient, coupon_in_db: dict, courier_in_db: dict, address_in_db: dict, book_in_db: dict):
    payload = {
        "address_id": address_in_db['address']["id"],
        "coupon_code": coupon_in_db["code"],
        "courier_id": courier_in_db["id"],
        "is_full_paid": True,
        "order_items": [
            {
                "book_id": book_in_db["id"],
                "quantity": 1
            }
        ],
        "payment_method": "bkash"
    }
    response = await client.post("/checkout/summary", json=payload)
    assert response.status_code == status.HTTP_200_OK
    assert response.json().keys() == {
        'sub_total', 'shipping_charge', 'weight_charge', 'discount', 'coupon_code'}
