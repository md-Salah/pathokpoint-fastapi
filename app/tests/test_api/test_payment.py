import pytest
from httpx import AsyncClient
from starlette import status
from unittest.mock import patch

pytestmark = pytest.mark.asyncio


@patch("app.library.bkash.create_payment")
@patch("app.library.bkash.grant_token")
async def test_pay_with_bkash(grant_token, create_payment, client: AsyncClient, order_in_db: dict):
    grant_token.return_value = 'token'
    create_payment.return_value = {'bkashURL': 'https://example.com'}
    res = await client.get('/payment/bkash?order_id={}'.format(order_in_db['id']))
    assert res.status_code == status.HTTP_200_OK
    assert res.json() == 'https://example.com'


@patch("app.library.bkash.execute_payment")
@patch("app.library.bkash.grant_token")
@patch("app.api.payment.email_service.payment_recieved_email")
async def test_pay_with_bkash_success_callback(payment_received, grant_token, execute_payment, client: AsyncClient, order_in_db: dict, payment_gateway_in_db: dict):
    grant_token.return_value = 'token'
    execute_payment.return_value = {
        "customerMsisdn": "01770618575",
        "trxID": "6H7801QFYM",
        "amount": "15",
        "merchantInvoiceNumber": str(order_in_db['invoice']),
        "statusMessage": "Successful",
    }
    payment_received.return_value = None

    res = await client.get('/payment/bkash/callback?paymentID=123&status=success&signature=123')
    assert res.status_code == status.HTTP_307_TEMPORARY_REDIRECT
    assert res.headers['location'].endswith(
        '/checkout/success?invoice={}&id={}'.format(order_in_db['invoice'], order_in_db['id']))


async def test_pay_with_bkash_failed_callback(client: AsyncClient):
    res = await client.get('/payment/bkash/callback?paymentID=123&status=failure&signature=123')
    assert res.status_code == status.HTTP_307_TEMPORARY_REDIRECT
    assert res.headers['location'].endswith('/checkout/failed')
