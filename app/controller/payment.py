from fastapi import Request, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
import logging
from uuid import UUID
import json

import app.library.bkash as bkash
from app.controller.exception import PaymentGatewayException
from app.models import Order
from app.controller.exception import BadRequestException, ServerErrorException, PaymentRequiredException
from app.pydantic_schema.transaction import CreateTransaction as CreateTransactionSchema
import app.controller.order as order_service
import app.controller.redis as redis_service
import app.controller.utility as utility_service
import app.controller.email as email_service

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
    redis_data = await redis_service.get_redis(request, payment_id)
    if not redis_data:
        logger.error('Bkash Payment ID is invalid.')
        raise BadRequestException('Invalid payment id.')
    bg_task.add_task(redis_service.delete_redis, request, payment_id)

    order_payload = utility_service.convert_str_to_uuid(json.loads(redis_data))
    if not isinstance(order_payload, dict):
        logger.error('Order payload from redis is not a dict type.')
        raise ServerErrorException(
            'Something went wrong, please try again later.')

    if status != "success":
        if order_payload['address']['email']:
            bg_task.add_task(email_service.order_failed_email,
                             order_payload['address']['email'])
        logger.error('Bkash payment failed. status: {}'.format(status))
        raise PaymentRequiredException(
            'Payment failed. Please try again later.')

    token = await bkash.grant_token()
    if not token:
        raise PaymentGatewayException(
            "Payment gateway error. Please try again later.")

    payment = await bkash.execute_payment(payment_id, token)
    if not payment:
        raise PaymentGatewayException(
            "Payment gateway error. Please try again later.")

    if payment['statusMessage'] == 'Successful':
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
        return order

    # Failed
    if order_payload['address']['email']:
        bg_task.add_task(email_service.order_failed_email,
                         order_payload['address']['email'])
    logger.error('Bkash execute payment failed. response: {}'.format(payment))
    raise PaymentRequiredException('Payment failed. Please try again later.')
