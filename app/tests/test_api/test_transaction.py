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


async def test_create_manual_transaction_by_admin(client: AsyncClient, payment_gateway_in_db: dict, book_in_db: dict, admin_auth_headers: dict):
    response = await client.post("/order/admin/new", json={
        "order_items": [
            {
                "book_id": book_in_db["id"],
                "quantity": 1,
            }
        ],
        "transactions": [{
            "payment_method": payment_gateway_in_db["name"],
            "amount": 250,
            "transaction_id": "UIOOE98709",
            "account_number": "01710002000",
        }]
    }, headers=admin_auth_headers)
    assert response.status_code == status.HTTP_201_CREATED
    return response.json()["transactions"][0]


async def test_delete_transaction(client: AsyncClient, transaction_in_db: dict, admin_auth_headers: dict):
    response = await client.delete("/transaction/{}".format(transaction_in_db['id']), headers=admin_auth_headers)
    assert response.status_code == status.HTTP_204_NO_CONTENT
