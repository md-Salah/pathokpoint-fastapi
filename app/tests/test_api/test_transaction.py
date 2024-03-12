import pytest
import pytest_asyncio
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

@pytest_asyncio.fixture(name="payment_gateway_in_db")
async def create_payment_gateway(client: AsyncClient):
    response = await client.post("/payment_gateway", json={"name": "test-gateway"})
    assert response.status_code == status.HTTP_201_CREATED
    return response.json()

@pytest_asyncio.fixture(name="transaction_in_db")
async def create_transaction(client: AsyncClient, payment_gateway_in_db: dict):
    payload = {
        **simple_transaction,
        "gateway": payment_gateway_in_db["id"]
    }
    response = await client.post("/transaction", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    return response.json()


async def test_get_transaction_by_id(client: AsyncClient, transaction_in_db: dict):
    response = await client.get(f"/transaction/id/{transaction_in_db['id']}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json().items() >= transaction_in_db.items()


async def test_get_all_transactions(client: AsyncClient, transaction_in_db: dict):
    response = await client.get("/transactions")
    assert len(response.json()) == 1
    assert response.json()[0].items() >= simple_transaction.items()


async def test_create_transaction(client: AsyncClient, payment_gateway_in_db: dict):
    payload = {
        **simple_transaction,
        "gateway": payment_gateway_in_db["id"]
    }
    response = await client.post("/transaction", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json().items() >= simple_transaction.items()


async def test_create_duplicate_transaction(client: AsyncClient, transaction_in_db: dict):
    payload = {
        **simple_transaction,
        "gateway": transaction_in_db["gateway"]["id"]
    }
    response = await client.post("/transaction", json=payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Transaction with transaction id ({}) already exists".format(simple_transaction['transaction_id'])}

async def test_create_refund_transaction(client: AsyncClient, payment_gateway_in_db: dict, user_in_db: dict):
    payload = {
        **simple_transaction,
        "gateway": payment_gateway_in_db["id"],
        "refunded_by": user_in_db["user"]["id"],
    }
    response = await client.post("/refund", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json().items() >= simple_transaction.items()

async def test_delete_transaction(client: AsyncClient, transaction_in_db: dict):
    id = transaction_in_db['id']
    response = await client.delete(f"/transaction/{id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    response = await client.get(f"/transaction/id/{id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND
