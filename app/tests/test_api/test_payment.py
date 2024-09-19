import pytest
from httpx import AsyncClient
from starlette import status
from unittest.mock import MagicMock
import json
import uuid

pytestmark = pytest.mark.asyncio


async def test_pay_with_bkash_success_callback(
    delete_redis: MagicMock,
    get_redis: MagicMock,
    bkash_exec_payment: MagicMock,
    send_email: MagicMock,
    client: AsyncClient,
    payment_gateway_in_db: dict,
    coupon_in_db: dict,
    address_payload: dict,
    courier_in_db: dict,
    book_in_db: dict
):

    order_payload = {
        "coupon_code": coupon_in_db["code"],
        "address": address_payload,
        "courier_id": courier_in_db["id"],
        "payment_method": "bkash",
        "order_items": [
            {
                "book_id": book_in_db["id"],
                "quantity": 1,
            }
        ],
        "is_full_paid": True
    }

    delete_redis.return_value = None
    get_redis.return_value = '{}'.format(json.dumps(
        order_payload
    ))
    bkash_exec_payment.return_value = {
        "customerMsisdn": "01770618575",
        "trxID": "6H7801QFYM",
        "amount": "15",
        "merchantInvoiceNumber": str(uuid.uuid4()),
        "statusMessage": "Successful",
    }
    send_email.return_value = None
    res = await client.get("/payment/bkash/callback", params={
        'paymentID': "TESTPAYMENTID",
        'status': "success",
        'signature': "some_signature"
    })

    assert res.status_code == status.HTTP_307_TEMPORARY_REDIRECT
    assert '/checkout/success' in res.headers['location']
    send_email.assert_called_once()
    
    
async def test_pay_with_bkash_failed_callback(
    delete_redis: MagicMock,
    get_redis: MagicMock,
    bkash_exec_payment: MagicMock,
    send_email: MagicMock,
    client: AsyncClient,
    payment_gateway_in_db: dict,
    coupon_in_db: dict,
    address_payload: dict,
    courier_in_db: dict,
    book_in_db: dict
):

    order_payload = {
        "coupon_code": coupon_in_db["code"],
        "address": address_payload,
        "courier_id": courier_in_db["id"],
        "payment_method": "bkash",
        "order_items": [
            {
                "book_id": book_in_db["id"],
                "quantity": 1,
            }
        ],
        "is_full_paid": True
    }

    delete_redis.return_value = None
    get_redis.return_value = '{}'.format(json.dumps(
        order_payload
    ))
    bkash_exec_payment.return_value = {
        "customerMsisdn": "01770618575",
        "trxID": "6H7801QFYM",
        "amount": "15",
        "merchantInvoiceNumber": str(uuid.uuid4()),
        "statusMessage": "Successful",
    }
    send_email.return_value = None
    res = await client.get("/payment/bkash/callback", params={
        'paymentID': "TESTPAYMENTID",
        'status': "failed",
        'signature': "some_signature"
    })

    assert res.status_code == status.HTTP_307_TEMPORARY_REDIRECT
    assert '/checkout/failed' in res.headers['location']
    send_email.assert_called_once()
    
    
async def test_pay_with_bkash_callback_failed_to_execute_payment(
    delete_redis: MagicMock,
    get_redis: MagicMock,
    bkash_exec_payment: MagicMock,
    send_email: MagicMock,
    client: AsyncClient,
    payment_gateway_in_db: dict,
    coupon_in_db: dict,
    address_payload: dict,
    courier_in_db: dict,
    book_in_db: dict
):

    order_payload = {
        "coupon_code": coupon_in_db["code"],
        "address": address_payload,
        "courier_id": courier_in_db["id"],
        "payment_method": "bkash",
        "order_items": [
            {
                "book_id": book_in_db["id"],
                "quantity": 1,
            }
        ],
        "is_full_paid": True
    }

    delete_redis.return_value = None
    get_redis.return_value = '{}'.format(json.dumps(
        order_payload
    ))
    bkash_exec_payment.return_value = {
        "customerMsisdn": "01770618575",
        "trxID": "6H7801QFYM",
        "amount": "15",
        "merchantInvoiceNumber": str(uuid.uuid4()),
        "statusMessage": "Failed",
    }
    send_email.return_value = None
    res = await client.get("/payment/bkash/callback", params={
        'paymentID': "TESTPAYMENTID",
        'status': "success",
        'signature': "some_signature"
    })

    assert res.status_code == status.HTTP_307_TEMPORARY_REDIRECT
    assert '/checkout/failed' in res.headers['location']
    send_email.assert_called_once()

