from sqlalchemy.ext.asyncio import AsyncSession
import traceback
import logging
from uuid import UUID
from sqlalchemy import select

import app.library.bkash as bkash
from app.controller.exception import ServerErrorException
from app.models import Order, OrderStatus
from app.controller.exception import NotFoundException
from app.pydantic_schema.transaction import CreateTransaction as CreateTransactionSchema
import app.controller.transaction as transaction_service
from app.constant.orderstatus import Status


logger = logging.getLogger(__name__)


async def pay_with_bkash(order_id: UUID, callback_url: str, db: AsyncSession) -> str:
    order = await db.get(Order, order_id)
    if not order:
        raise NotFoundException('Order not found', str(order_id))
    payload = {
        "mode": "0011",
        "payerReference": order.address.name if (await order.awaitable_attrs.address) else 'Anonymous',
        "callbackURL": callback_url,
        "amount": str(int(order.due if order.is_full_paid else 100)),
        "currency": "BDT",
        "intent": "sale",
        "merchantInvoiceNumber": str(order.invoice),
    }
    try:
        token = await bkash.grant_token()
        data = await bkash.create_payment(token, payload=payload)
        return data['bkashURL']
    except Exception as err:
        logger.error(traceback.format_exc())
        raise ServerErrorException(str(err))


async def execute_payment(payment_id: str, db: AsyncSession) -> Order | None:
    try:
        token = await bkash.grant_token()
        data = await bkash.execute_payment(payment_id, token)
    except Exception:
        logger.error(traceback.format_exc())
        raise ServerErrorException('Bkash payment failed. Try again later.')

    if data and data['statusMessage'] == 'Successful':
        order = await db.scalar(select(Order).filter(Order.invoice == int(data['merchantInvoiceNumber'])))
        if not order:
            raise NotFoundException(
                'Order not found', data['merchantInvoiceNumber'])

        payload = CreateTransactionSchema(
            payment_method='bkash',
            amount=data['amount'],
            transaction_id=data['trxID'],
            reference=data['merchantInvoiceNumber'],
            account_number=data['customerMsisdn']
        )
        payload = payload.model_dump()
        payload['customer'] = await order.awaitable_attrs.customer
        payload['is_manual'] = False
        trx = await transaction_service.validate_transaction(payload, db)

        (await order.awaitable_attrs.transactions).append(trx)
        order.paid += trx.amount
        order.due = max(0, order.net_amount - order.paid)

        if order.order_status[-1].status == Status.pending:
            order.order_status.append(OrderStatus(
                status=Status.processing
            ))
        await db.commit()
        return order
    elif data:
        logger.error('Bkash payment failed. statusMessage: {}'.format(
            data.get('statusMessage')))
    return None
