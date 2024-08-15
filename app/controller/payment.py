from sqlalchemy.ext.asyncio import AsyncSession
import traceback
import logging
from uuid import UUID
from sqlalchemy import select

import app.library.bkash as bkash
from app.controller.exception import ServerErrorException
from app.models import Order, PaymentGateway, Transaction, OrderStatus
from app.controller.exception import NotFoundException, ConflictException
from app.pydantic_schema.transaction import CreateTransaction as CreateTransactionSchema
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


async def execute_payment(payment_id: str, db: AsyncSession) -> str | None:
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

        gateway = await db.scalar(select(PaymentGateway).filter(PaymentGateway.name == 'bkash'))
        if not gateway:
            raise NotFoundException('Payment gateway not found', 'bkash')

        _trx = await db.scalar(select(Transaction).filter(Transaction.transaction_id == data['trxID']))
        if _trx:
            raise ConflictException('Duplicate transaction id', data['trxID'])

        payload = CreateTransactionSchema(
            amount=data['amount'],
            transaction_id=data['trxID'],
            reference=data['merchantInvoiceNumber'],
            account_number=data['customerMsisdn'],
            is_manual=False,
            gateway_id=gateway.id,
            order_id=order.id,
            customer_id=None,
        )

        trx = Transaction(**payload.model_dump())
        (await order.awaitable_attrs.transactions).append(trx)
        order.paid += trx.amount
        order.due = order.net_amount - order.paid + order.payment_reversed

        if order.order_status[-1].status == Status.pending_payment:
            order.order_status.append(OrderStatus(
                status=Status.order_confirmed
            ))
        await db.commit()
        return str(order.invoice)
    elif data:
        logger.error('Bkash payment failed. statusMessage: {}'.format(data.get('statusMessage')))
    return None
