from httpx import AsyncClient
import logging
import traceback

from app.config.settings import settings

logger = logging.getLogger(__name__)


async def grant_token() -> str | None:
    url = f'{settings.BKASH_URL}/tokenized/checkout/token/grant'
    payload = {
        "app_key": settings.BKASH_APP_KEY,
        "app_secret": settings.BKASH_APP_SECRET
    }
    headers = {
        'Content-Type': "application/json",
        'Accept': "application/json",
        'username': settings.BKASH_USERNAME,
        'password': settings.BKASH_PASSWORD
    }
    try:
        async with AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
            if response.status_code != 200:
                logger.error(
                    'Failed to init bkash grant token, response: %s', response.text)
                return None
            return response.json()['id_token']
    except Exception:
        logger.error(traceback.format_exc())
    return None


async def initiate_payment(id_token: str, payload: dict) -> dict | None:
    url = f"{settings.BKASH_URL}/tokenized/checkout/create"
    headers = {
        'Content-Type': "application/json",
        'Accept': "application/json",
        'Authorization': f"Bearer {id_token}",
        'X-APP-Key': settings.BKASH_APP_KEY,
    }
    try:
        async with AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
            if response.status_code != 200:
                logger.error(
                    'Failed to create bkash payment, response: %s', response.text)
                return None
            return response.json()
    except Exception:
        logger.error(traceback.format_exc())
        return None


async def execute_payment(payment_id: str, id_token: str) -> dict | None:
    url = f"{settings.BKASH_URL}/tokenized/checkout/execute"
    headers = {
        'Accept': "application/json",
        'Authorization': f"Bearer {id_token}",
        'X-APP-Key': settings.BKASH_APP_KEY,
    }
    payload = {
        "paymentID": payment_id
    }
    try:
        async with AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
            if response.status_code != 200:
                logger.error(
                    'Failed to execute bkash payment, response: %s', response.text)
                return None
            return response.json()
    except Exception:
        logger.error(traceback.format_exc())
        return None
