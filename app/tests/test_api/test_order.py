import pytest
from httpx import AsyncClient
from starlette import status
from typing import Any

pytestmark = pytest.mark.asyncio


async def test_get_my_order_by_id(client: AsyncClient, address_in_db: dict[str, Any], courier_in_db: dict, book_in_db: dict):
    user_in_db = address_in_db['user']
    headers = {'Authorization': 'Bearer {}'.format(
        user_in_db['token']['access_token'])}
    payload = {
        "address": address_in_db['address'],
        "courier_id": courier_in_db["id"],
        "payment_method": "bkash",
        "order_items": [
            {
                "book_id": book_in_db["id"],
                "quantity": 1,
            }
        ]
    }
    response = await client.post("/order/new", json=payload, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED
    order_in_db = response.json()

    response = await client.get(f"/order/id/{order_in_db['id']}", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json().items() <= order_in_db.items()


async def test_get_order_of_other_customer(client: AsyncClient, order_in_db: dict, customer_auth_headers: dict):
    response = await client.get(f"/order/id/{order_in_db['id']}", headers=customer_auth_headers)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


async def test_get_order_by_id_admin(client: AsyncClient, order_in_db: dict, admin_auth_headers: dict):
    response = await client.get(f"/order/admin/id/{order_in_db['id']}", headers=admin_auth_headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json().items() >= order_in_db.items()


@pytest.mark.parametrize("query_string_template, expected_length, modify_query_string", [
    ("", 1, lambda qs, _: qs),
    ("?order_status__status=pending-payment", 1, lambda qs, _: qs),
    ("?customer__email=admin@gmail.com", 0, lambda qs, _: qs),
])
async def test_get_all_orders_by_admin(client: AsyncClient, order_in_db: dict, admin_auth_headers: dict, query_string_template: str, expected_length: int, modify_query_string):
    query_string = modify_query_string(query_string_template, order_in_db)
    response = await client.get(f"/order/admin/all{query_string}", headers=admin_auth_headers)
    assert len(response.json()) == expected_length
    if expected_length:
        assert response.json()[0].items() >= order_in_db.items()
    assert response.headers.get("x-total-count") == str(expected_length)


@pytest.mark.parametrize("query_string_template, expected_length, modify_query_string", [
    ("", 0, lambda qs, _: qs),
    ("?order_status__status=pending-payment", 0, lambda qs, _: qs)
])
async def test_get_my_orders(client: AsyncClient, order_in_db: dict, customer_auth_headers: dict, query_string_template: str, expected_length: int, modify_query_string):
    query_string = modify_query_string(query_string_template, order_in_db)
    response = await client.get(f"/order/my-orders{query_string}", headers=customer_auth_headers)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == expected_length
    if expected_length:
        assert response.json()[0].items() <= order_in_db.items()
    assert response.headers.get("x-total-count") == str(expected_length)


@pytest.mark.parametrize('quantity', [1, 2])
async def test_create_order_by_customer(client: AsyncClient, user_in_db: dict[str, Any], book_in_db: dict, coupon_in_db: dict, address_payload: dict[str, Any], courier_in_db: dict, quantity: int):
    payload = {
        "coupon_code": coupon_in_db["code"],
        "address": address_payload,
        "courier_id": courier_in_db["id"],
        "payment_method": "bkash",
        "order_items": [
            {
                "book_id": book_in_db["id"],
                "quantity": quantity,
            }
        ]
    }

    response = await client.post("/order/new", json=payload, headers={
        'Authorization': 'Bearer {}'.format(user_in_db['token']['access_token'])
    })
    response_data = response.json()

    assert response.status_code == status.HTTP_201_CREATED
    assert len(response_data["order_items"]) == len(payload["order_items"])
    assert response_data["coupon"]["code"] == payload["coupon_code"]
    assert response_data["address"].items() >= payload["address"].items()
    assert response_data["courier"]["id"] == payload["courier_id"]

    # Status
    assert len(response_data["order_status"]) == 1
    assert response_data["order_status"][0]["status"] == "pending-payment"

    # Payment
    assert response_data['paid'] == 0

    # Stock
    response = await client.get(f"/book/id/{book_in_db['id']}")
    assert response.json()["quantity"] == book_in_db["quantity"] - quantity

    # Shipping charge
    assert response_data['shipping_charge'] == courier_in_db['base_charge']
    assert response_data['weight_charge'] == courier_in_db['weight_charge_per_kg'] * (
        book_in_db['weight_in_gm']/1000) * quantity

    # Discount
    if coupon_in_db['discount_type'] == 'percentage':
        if book_in_db['sale_price'] * quantity < coupon_in_db['min_spend_old']:
            assert response_data['discount'] == 0
        else:
            assert response_data['discount'] == book_in_db['sale_price'] * \
                quantity * (coupon_in_db['discount_old'] / 100)


async def test_create_order_by_admin_without_shipping(client: AsyncClient, book_in_db: dict, admin_auth_headers: dict):
    payload = {
        "order_items": [
            {
                "book_id": book_in_db["id"],
                "quantity": 1,
            }
        ]
    }

    response = await client.post("/order/admin/new", json=payload, headers=admin_auth_headers)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()['shipping_charge'] == 0.0
    assert response.json()['weight_charge'] == 0.0
    assert response.json()['total'] == book_in_db['sale_price']


@pytest.mark.parametrize('quantity', [1, 2])
async def test_create_order_with_fixed_discount(client: AsyncClient, book_in_db: dict, quantity: int, admin_auth_headers: dict):
    response = await client.post("/coupon", json={
        'code': 'FIXED',
        'discount_type': 'fixed-amount',
        'discount_old': 100,  # 100 tk off on order above 300
        'discount_new': 0,
        'min_spend_old': 300,
    }, headers=admin_auth_headers)
    assert response.status_code == status.HTTP_201_CREATED
    coupon_in_db = response.json()

    payload = {
        'coupon_code': coupon_in_db['code'],
        'order_items': [
            {
                'book_id': book_in_db['id'],
                'quantity': quantity,
            }
        ]
    }

    response = await client.post("/order/admin/new", json=payload, headers=admin_auth_headers)
    assert response.status_code == status.HTTP_201_CREATED

    if book_in_db['sale_price'] * quantity < coupon_in_db['min_spend_old']:
        assert response.json()['discount'] == 0
    else:
        assert response.json()['discount'] == coupon_in_db['discount_old']


async def test_update_order_status(client: AsyncClient, order_in_db: dict, admin_auth_headers: dict):
    assert len(order_in_db['order_status']) == 1
    payload = {
        "order_status": {
            "status": "order-confirmed",
            "note": "payment received, preparing for shipment"
        }
    }

    response = await client.patch(f"/order/{order_in_db['id']}", json=payload, headers=admin_auth_headers)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()['order_status']) == 2


async def test_update_order_payment_by_admin(client: AsyncClient, order_in_db: dict, payment_gateway_in_db: dict, admin_auth_headers: dict):
    # response = await client.post("/transaction/make-payment", json={
    #     "amount": 150,
    #     "transaction_id": '123456',
    #     'account_number': '+8801234567890',
    #     'gateway_id': payment_gateway_in_db['id'],
    #     'order_id': order_in_db['id']
    # })
    # assert response.status_code == status.HTTP_201_CREATED
    # transaction_in_db = response.json()

    # response = await client.patch(f"/order/{order_in_db['id']}", json={
    #     'transaction_id': transaction_in_db['id']
    # }, headers=admin_auth_headers)
    # assert response.status_code == status.HTTP_200_OK
    # assert response.json()['paid'] == transaction_in_db['amount']
    pass


async def test_update_order_item_by_admin(client: AsyncClient, order_in_db: dict, book_in_db: dict, admin_auth_headers: dict):
    response = await client.patch(f"/order/{order_in_db['id']}", json={
        'order_items': [
            {
                'book_id': book_in_db['id'],
                'quantity': 2
            }
        ]
    }, headers=admin_auth_headers)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()['order_items']) == 1
    assert response.json()['total'] == book_in_db['sale_price'] * 2


async def test_delete_order(client: AsyncClient, order_in_db: dict, admin_auth_headers: dict):
    response = await client.delete("/order/{}".format(order_in_db['id']), headers=admin_auth_headers)
    assert response.status_code == status.HTTP_204_NO_CONTENT
