# import app.pydantic_schema.order as schema
# import app.controller.order as order_service
# from fastapi import APIRouter, Depends, Query, Path, Response, HTTPException
# from typing import List
# from sqlalchemy.ext.asyncio import AsyncSession
# from uuid import UUID

# from app.config.database import get_db

# router = APIRouter()

# # Admin | Customer(creator) : GET order by id
# @router.get('/order/{id}', response_model=schema.ReadOrder)
# async def get_order_by_id(id: UUID, db: AsyncSession = Depends(get_db)):
#     return await order_service.get_order_by_id(id, db)

# # Admin: GET all orders
# @router.get('/orders/', response_model=List[schema.ReadOrder])
# async def get_all_orders(*, page: int = Query(1, ge=1), per_page: int = Query(10, ge=1, le=100), db: AsyncSession = Depends(get_db),  response: Response):
#     orders = await order_service.get_all_orders(page, per_page, db)
#     total_books = await order_service.count_order(db)

#     response.headers['X-Total-Count'] = str(total_books)
#     response.headers['X-Total-Pages'] = str(-(-total_books // per_page))
#     response.headers['X-Current-Page'] = str(page)
#     response.headers['X-Per-Page'] = str(per_page)

#     return orders

# # Customer: CREATE order
# @router.post('/order/', response_model=schema.ReadOrder)
# async def create_order(payload: schema.CreateOrder, db: AsyncSession = Depends(get_db)):
#     return await order_service.create_order(payload, db)

# # Admin: UPDATE order
# @router.put('/order/{id}', response_model=schema.ReadOrder)
# async def update_order(id: UUID, payload: schema.UpdateOrder, db: AsyncSession = Depends(get_db)):
#     return await order_service.update_order(id, payload, db)

# # Admin: DELETE order
# @router.delete('/order/{id}', response_model=schema.DeleteOrder)
# async def delete_order(id: UUID, db: AsyncSession = Depends(get_db)):
#     return await order_service.delete_order(id, db)

# # Admin: Search order
# @router.get('/order/search/{q}', response_model=List[schema.ReadOrder])
# async def search_order(q: str = Path(..., min_length=3), db: AsyncSession = Depends(get_db)):
#     return await order_service.search_orders(q, db)
