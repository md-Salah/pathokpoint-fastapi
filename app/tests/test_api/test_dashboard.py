import pytest
from httpx import AsyncClient
from starlette import status

pytestmark = pytest.mark.asyncio


async def test_order_analysis(client: AsyncClient, admin_auth_headers: dict[str, str]):
    response = await client.get("/dashboard/order", headers=admin_auth_headers)
    assert response.status_code == status.HTTP_200_OK


async def test_inventory_analysis(client: AsyncClient, admin_auth_headers: dict[str, str]):
    response = await client.get("/dashboard/inventory", headers=admin_auth_headers)
    assert response.status_code == status.HTTP_200_OK
