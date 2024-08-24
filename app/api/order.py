from fastapi import APIRouter, status, Query, Response
from uuid import UUID
from fastapi_filter import FilterDepends


from app.filter_schema.order import OrderFilter, OrderFilterCustomer
from app.controller.exception import BadRequestException
from app.controller.auth import AccessToken, AdminAccessToken, AccessTokenOptional
import app.pydantic_schema.order as schema
from app.config.database import Session
import app.controller.order as order_service

router = APIRouter(prefix='/order')


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


@router.post('/new', response_model=schema.OrderOut, status_code=status.HTTP_201_CREATED)
async def create_order(payload: schema.CreateOrder, token: AccessTokenOptional, db: Session):
    data = payload.model_dump()
    if token:
        data['customer_id'] = token['id']
    return await order_service.create_order(data, db)


@router.post('/admin/new', response_model=schema.OrderOutAdmin, status_code=status.HTTP_201_CREATED)
async def create_order_by_admin(payload: schema.CreateOrderAdmin, _: AdminAccessToken, db: Session):
    return await order_service.create_order(payload.model_dump(), db)


@router.patch('/{id}', response_model=schema.OrderOutAdmin)
async def update_order(id: UUID, payload: schema.UpdateOrderAdmin, _: AdminAccessToken, db: Session):
    return await order_service.update_order(id, payload.model_dump(exclude_unset=True), db)


@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(id: UUID, _: AdminAccessToken, db: Session, restock: bool = Query(False)):
    await order_service.delete_order(id, restock, db)


# @router.post('/{id}/invoice')
# async def send_invoice_email(id: UUID, db: Session):
#     order = await order_service.get_order_by_id(id, db)
#     customer = await order.awaitable_attrs.customer
#     if customer:
#         return await email_service.send_invoice_email(order)
#     else:
#         raise bad_request_exception(
#             str(id), 'Guest order does not have email address')
