from fastapi import APIRouter, status, Query, Response
from uuid import UUID
from fastapi_filter import FilterDepends


from app.filter_schema.order import OrderFilter
from app.controller.exception import bad_request_exception
from app.controller.auth import AccessToken
import app.pydantic_schema.order as schema
from app.config.database import Session
import app.controller.order as order_service
import app.controller.email as email_service

router = APIRouter(prefix='/order')


@router.get('/id/{id}', response_model=schema.OrderOut)
async def get_order_by_id(id: UUID, db: Session):
    return await order_service.get_order_by_id(id, db)


@router.get('/admin/id/{id}', response_model=schema.OrderOutAdmin)
async def get_order_by_id_admin(id: UUID, db: Session):
    return await order_service.get_order_by_id(id, db)


@router.get('/admin/all', response_model=list[schema.OrderOutAdmin])
async def get_all_orders(*,
                         page: int = Query(1, ge=1),
                         per_page: int = Query(10, ge=1, le=100),
                         filter: OrderFilter = FilterDepends(OrderFilter),
                         db: Session,
                         response: Response):
    orders = await order_service.get_all_orders(filter, page, per_page, db)
    total_orders = await order_service.count_orders(filter, db)

    response.headers['X-Total-Count'] = str(total_orders)
    response.headers['X-Total-Pages'] = str(-(-total_orders // per_page))
    response.headers['X-Current-Page'] = str(page)
    response.headers['X-Per-Page'] = str(per_page)

    return orders


@router.post('/new', response_model=schema.OrderOut, status_code=status.HTTP_201_CREATED)
async def create_order(payload: schema.CreateOrder, token: AccessToken, db: Session):
    data = {
        **payload.model_dump(),
        'customer_id': token['id']
    }
    return await order_service.create_order(data, db)


@router.post('/admin/new', response_model=schema.OrderOutAdmin, status_code=status.HTTP_201_CREATED)
async def create_order_by_admin(payload: schema.CreateOrderAdmin, db: Session):
    return await order_service.create_order(payload.model_dump(), db)


@router.patch('/{id}', response_model=schema.OrderOutAdmin)
async def update_order(id: UUID, payload: schema.UpdateOrderAdmin, db: Session):
    return await order_service.update_order(id, payload.model_dump(exclude_unset=True), db)


@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(id: UUID, db: Session):
    await order_service.delete_order(id, db)


@router.post('/{id}/invoice')
async def send_invoice_email(id: UUID, db: Session):
    order = await order_service.get_order_by_id(id, db)
    customer = await order.awaitable_attrs.customer
    if customer:
        return await email_service.send_invoice_email(order)
    else:
        raise bad_request_exception(
            str(id), 'Guest order does not have email address')
