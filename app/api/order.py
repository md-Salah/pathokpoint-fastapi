from fastapi import APIRouter, status, Query, Response, Request, BackgroundTasks
from uuid import UUID
from fastapi_filter import FilterDepends
import json
import logging

from app.filter_schema.order import OrderFilter, OrderFilterCustomer
from app.controller.exception import BadRequestException
from app.controller.auth import AccessToken, AdminAccessToken, AccessTokenOptional, CurrentAdmin
import app.pydantic_schema.order as schema
from app.config.database import Session
import app.controller.order as order_service
import app.controller.email as email_service
import app.controller.redis as redis_service
import app.controller.payment as payment_service
import app.controller.utility as utility_service

router = APIRouter(prefix='/order')

logger = logging.getLogger(__name__)


@router.get('/id/{id}', response_model=schema.OrderOut)
async def get_order_by_id(id: UUID, token: AccessToken, db: Session):
    order = await order_service.get_order_by_id(id, db)
    if order.customer_id != token['id']:
        raise BadRequestException('This order does not belong to you')
    return order


@router.get('/admin/id/{id}', response_model=schema.OrderOutAdmin)
async def get_order_by_id_admin(id: UUID, _: AdminAccessToken, db: Session):
    return await order_service.get_order_by_id(id, db)


@router.get('/admin/invoice/{invoice}', response_model=schema.OrderOutAdmin)
async def get_order_by_invoice_admin(invoice: str, _: AdminAccessToken, db: Session):
    try:
        invoice_int = int(invoice)
    except ValueError:
        raise BadRequestException('Invalid invoice number')
    return await order_service.get_order_by_invoice(invoice_int, db)


@router.get('/my-orders', response_model=list[schema.OrderOut])
async def get_my_orders(*,
                        page: int = Query(1, ge=1),
                        per_page: int = Query(10, ge=1, le=100),
                        filter: OrderFilterCustomer = FilterDepends(
                            OrderFilterCustomer),
                        db: Session,
                        token: AccessToken,
                        response: Response):
    orders, total_orders = await order_service.get_my_orders(filter, token['id'], page, per_page, db)

    response.headers['X-Total-Count'] = str(total_orders)
    response.headers['X-Total-Pages'] = str(-(-total_orders // per_page))
    response.headers['X-Current-Page'] = str(page)
    response.headers['X-Per-Page'] = str(per_page)

    return orders


@router.get('/admin/all', response_model=list[schema.OrderOutAdmin])
async def get_all_orders_by_admin(*,
                                  page: int = Query(1, ge=1),
                                  per_page: int = Query(10, ge=1, le=100),
                                  filter: OrderFilter = FilterDepends(
                                      OrderFilter),
                                  _: AdminAccessToken,
                                  db: Session,
                                  response: Response):
    orders, total_orders = await order_service.get_all_orders(filter, page, per_page, db)

    response.headers['X-Total-Count'] = str(total_orders)
    response.headers['X-Total-Pages'] = str(-(-total_orders // per_page))
    response.headers['X-Current-Page'] = str(page)
    response.headers['X-Per-Page'] = str(per_page)

    return orders


@router.post('/new', response_model=schema.PaymentUrlResponse)
async def create_order(payload: schema.CreateOrder, token: AccessTokenOptional, request: Request, db: Session):
    req_payload = payload.model_dump()
    if token:
        req_payload['customer_id'] = token['id']
    order = await order_service.create_order(req_payload, db, commit=False)

    # Payment
    EXPIRE_SEC = 10 * 60
    MIN_AMOUNT = 100
    if req_payload['payment_method'] == 'bkash':
        callback_url = str(request.url_for('pay_with_bkash_callback'))
        payment = await payment_service.initiate_bkash_payment(
            order.id,
            int(order.net_amount if order.is_full_paid else MIN_AMOUNT),
            order.address.name if order.address else str(order.id),
            callback_url
        )

        await redis_service.set_redis(request, payment['payment_id'], json.dumps(
            utility_service.convert_uuid_to_str(req_payload)
        ), EXPIRE_SEC)
        return {"payment_url": payment['payment_url']}
    else:
        raise BadRequestException('Invalid payment method')


@router.post('/admin/new', response_model=schema.OrderOutAdmin, status_code=status.HTTP_201_CREATED)
async def create_order_by_admin(payload: schema.CreateOrderAdmin, _: AdminAccessToken, bg_task: BackgroundTasks, db: Session):
    req_payload = payload.model_dump()
    for trx in req_payload['transactions']:
        trx['is_manual'] = True  # Transaction is verified manually by admin
    order = await order_service.create_order(req_payload, db)
    if order.address and order.address.email:
        bg_task.add_task(email_service.send_invoice_email, order)
    return order


@router.patch('/{id}', response_model=schema.OrderOutAdmin)
async def update_order(id: UUID, payload: schema.UpdateOrderAdmin, admin: CurrentAdmin, db: Session):
    logger.info("{} is updating order {}".format(admin, id))
    logger.info("Payload: {}".format(payload))
    return await order_service.update_order(id, payload.model_dump(exclude_unset=True), db)


@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(id: UUID, _: AdminAccessToken, db: Session, restock: bool = Query(False)):
    await order_service.delete_order(id, restock, db)


@router.post('/resend-invoice/{invoice}')
async def resend_invoice(invoice: str, _: AdminAccessToken, bg_task: BackgroundTasks, db: Session):
    order = await order_service.get_order_by_invoice(invoice, db)
    if order.address.email:
        bg_task.add_task(email_service.send_invoice_email, order)
    return {"message": "ok"}
