import json
import logging
import traceback
from uuid import UUID

from fastapi import BackgroundTasks, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import app.controller.email as email_service
import app.controller.order as order_service
import app.controller.redis as redis_service
import app.controller.utility as utility_service
import app.library.bkash as bkash
from app.config.settings import settings
from app.controller.exception import (
    PaymentGatewayException,
)
from app.models import Book, Order
from app.pydantic_schema.transaction import CreateTransaction as CreateTransactionSchema

logger = logging.getLogger(__name__)


async def initiate_bkash_payment(order_id: UUID, amount: int, reference: str, callback_url: str) -> dict:
    payload = {
        "mode": "0011",
        "payerReference": reference,
        "callbackURL": callback_url,
        "amount": str(amount),
        "currency": "BDT",
        "intent": "sale",
        "merchantInvoiceNumber": str(order_id),
    }

    token = await bkash.grant_token()
    if not token:
        raise PaymentGatewayException(
            "Payment gateway error. Please try again later.")

    payment = await bkash.initiate_payment(token, payload=payload)
    logger.debug('Init bkash payment: {}'.format(payment))
    if not payment:
        raise PaymentGatewayException(
            "Payment gateway error. Please try again later.")
    return {
        'payment_url': payment['bkashURL'],
        'payment_id': payment['paymentID']
    }


async def execute_payment(payment_id: str, status: str, request: Request, bg_task: BackgroundTasks, db: AsyncSession) -> Order | None:
    order_payload = None
    try:
        redis_data = await redis_service.get_redis(request, payment_id)
        assert redis_data, 'Bkash Payment ID is invalid.'
        bg_task.add_task(redis_service.delete_redis, request, payment_id)

        order_payload = utility_service.convert_str_to_uuid(
            json.loads(redis_data))
        assert isinstance(
            order_payload, dict), 'Order payload is invalid, not dict type.'

        assert status == 'success', 'Bkash payment failed. status: {}'.format(
            status)

        token = await bkash.grant_token()
        assert token, 'Payment gateway error. Token is not granted.'

        payment = await bkash.execute_payment(payment_id, token)
        assert payment, 'Payment gateway error. Failed to execute payment.'
        assert payment['statusMessage'] == 'Successful', 'Payment failed. status: {}'.format(
            payment['statusMessage'])

        payload = CreateTransactionSchema(
            payment_method='bkash',
            amount=payment['amount'],
            transaction_id=payment['trxID'],
            reference=payment['merchantInvoiceNumber'],
            account_number=payment['customerMsisdn']
        )
        payload = payload.model_dump()
        payload['is_manual'] = False  # Payment is verified by bkash API
        order_payload['transactions'] = [payload]

        order = await order_service.create_order(order_payload, db, commit=True,
                                                 order_id=payment['merchantInvoiceNumber'])
        bg_task.add_task(email_service.send_invoice_email, order)
        msg = email_service.MessageSchema(
            subject='New order received',
            recipients=settings.ADMIN_EMAILS,
            body=f'New order received. Order Invoice: {order.invoice}',
            subtype=email_service.MessageType.plain
        )
        bg_task.add_task(email_service.send_email, msg)
        return order

    except AssertionError as err:
        logger.error(err)
        if order_payload and isinstance(order_payload, dict):
            await order_failed_post_action(order_payload, bg_task, db)
    except Exception:
        logger.error(traceback.format_exc())
        if order_payload and isinstance(order_payload, dict):
            await order_failed_post_action(order_payload, bg_task, db)


async def order_failed_post_action(order_payload: dict, bg_task: BackgroundTasks, db: AsyncSession) -> None:
    if order_payload['address']['email']:
        await email_service.order_failed_email(
            order_payload['address']['email'])

    books = await db.scalars(select(Book).filter(Book.id.in_(
        [item['book_id'] for item in order_payload['order_items']]
    )))
    book_details = []
    for book in books:
        book_details.append('{}- {}- {}Tk'.format(
            book.public_id, book.name, book.sale_price
        ))

    body = '''
        {} Failed to order the following books:
        {}
        Contact the customer for further information.
        Phone: {}
        Email: {}
        '''.format(
        order_payload['address']['name'],
        '\n'.join(book_details),
        order_payload['address']['phone_number'],
        order_payload['address']['email']
    )

    msg = email_service.MessageSchema(
        subject="Order failed",
        recipients=settings.ADMIN_EMAILS,
        body=body,
        subtype=email_service.MessageType.plain
    )
    bg_task.add_task(email_service.send_email, msg)
