import app.pydantic_schema.order as schema
import app.controller.order as service
from fastapi import APIRouter
from fastapi import HTTPException
from typing import List

router = APIRouter()


# Admin | Customer(creator) : GET order by id
@router.get('/order/{id}', response_model=schema.ReadOrder)
async def get_order_by_id(id: int):
    order = await service.get_order_by_id(id)

    if order is None:
        raise HTTPException(status_code=404, detail='Order not found')
    return order


# Admin: GET all orders
@router.get('/orders/', response_model=List[schema.ReadOrder])
async def get_all_orders():
    return await service.get_all_orders()


# Customer: CREATE order
@router.post('/order/', response_model=schema.ReadOrder)
async def create_order(order: schema.CreateOrder):
    new_order = await service.create_order(order)

    return new_order


# Admin: UPDATE order
@router.put('/order/{id}', response_model=schema.ReadOrder)
async def update_order(id: int, order: schema.UpdateOrder):
    updated_order = await service.update_order(id, order)

    return updated_order


# Admin: DELETE order
@router.delete('/order/{id}', response_model=schema.DeleteOrder)
async def delete_order(id: int):
    return await service.delete_order(id)


# Admin: Search order
@router.get('/order/search/{key}', response_model=List[schema.ReadOrder])
async def search_order(key: str):
    return await service.search_order(key)