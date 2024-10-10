import pytest
from httpx import AsyncClient
from starlette import status
from unittest.mock import MagicMock

pytestmark = pytest.mark.asyncio


async def test_contact_us(client: AsyncClient, send_email: MagicMock):
    payload = {
        "name": "test user",
        "email": "testuser@gmail.com",
        "phone_number": "029883883838",
        "message": "test message",
    }
    response = await client.post("/misc/contact-us", json=payload)
    assert response.status_code == status.HTTP_200_OK
    send_email.assert_called_once()
