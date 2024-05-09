import pytest
from httpx import AsyncClient
from starlette import status

pytestmark = pytest.mark.asyncio

simple_transaction = {
    "amount": 150.0,
    "transaction_id": "some-transaction-id",
    "reference": "abdul kadir",
    "account_number": "+8801234567890",
    "is_manual": False,
}


async def test_get_transaction_by_id(client: AsyncClient, transaction_in_db: dict, admin_auth_headers: dict):
    response = await client.get(f"/transaction/id/{transaction_in_db['id']}", headers=admin_auth_headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json().items() >= transaction_in_db.items()


async def test_get_all_transactions(client: AsyncClient, transaction_in_db: dict, admin_auth_headers: dict):
    response = await client.get("/transaction/all", headers=admin_auth_headers)
    assert len(response.json()) == 1
    assert response.json()[0].items() >= transaction_in_db.items()


async def test_create_transaction(client: AsyncClient, payment_gateway_in_db: dict, order_in_db: dict):
    payload = {
        **simple_transaction,
        "gateway_id": payment_gateway_in_db["id"],
        "order_id": order_in_db["id"],
    }
    response = await client.post("/transaction/make-payment", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json().items() >= payload.items()


async def test_create_duplicate_transaction(client: AsyncClient, transaction_in_db: dict, order_in_db: dict):
    response = await client.post("/transaction/make-payment", json=transaction_in_db)
    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()['detail']['message'] == 'Transaction already exists'


async def test_create_manual_transaction(client: AsyncClient, payment_gateway_in_db: dict, order_in_db: dict, admin_auth_headers: dict):
    payload = {
        **simple_transaction,
        "gateway_id": payment_gateway_in_db["id"],
        "order_id": order_in_db["id"],
    }
    response = await client.post("/transaction/add-manual-payment", json=payload, headers=admin_auth_headers)
    assert response.status_code == status.HTTP_201_CREATED
    payload['is_manual'] = True
    assert response.json().items() >= payload.items()


async def test_create_refund_transaction(client: AsyncClient, payment_gateway_in_db: dict, user_in_db: dict, order_in_db: dict, admin_auth_headers: dict):
    payload = {
        **simple_transaction,
        "gateway_id": payment_gateway_in_db["id"],
        "refunded_by_id": user_in_db["user"]["id"],
        "order_id": order_in_db["id"],
    }
    response = await client.post("/transaction/refund", json=payload, headers=admin_auth_headers)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json().items() >= payload.items()


async def test_delete_transaction(client: AsyncClient, transaction_in_db: dict, admin_auth_headers: dict):
    response = await client.delete("/transaction/{}".format(transaction_in_db['id']), headers=admin_auth_headers)
    assert response.status_code == status.HTTP_204_NO_CONTENT
