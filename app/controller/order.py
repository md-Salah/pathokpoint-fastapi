# from fastapi import HTTPException, status
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy import select, func, delete, or_
# from uuid import UUID
# from typing import Sequence

# from app.models.order import Order
# import app.pydantic_schema.order as schema

# async def get_order_by_id(id: UUID, db: AsyncSession) -> schema.ReadOrder:
#     result = await db.execute(select(Order).where(Order.id == id))
#     order = result.scalar()
#     if not order:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
#                             detail=f'Order with id {id} not found')
#     return order


# async def get_all_orders(page: int, per_page: int, db: AsyncSession) -> Sequence[schema.ReadOrder]:
#     offset = (page - 1) * per_page
    
#     result = await db.execute(select(Order).offset(offset).limit(per_page))
#     orders = result.scalars().all()
#     return orders

# async def search_orders(q: str, db: AsyncSession) -> Sequence[schema.ReadOrder]:
#     result = await db.execute(select(Order).where(
#         or_(
#             Order.id.ilike(f'%{q}%'),
#             Order.reference.ilike(f'%{q}%'),
#         )
#     ))
#     orders = result.scalars().all()
#     orders = []
#     return orders


# async def create_order(payload: schema.CreateOrder, db: AsyncSession) -> schema.ReadOrder:
#     new_order = Order(**schema.CreateOrder.model_dump(payload))
#     db.add(new_order)
#     await db.commit()

#     return new_order


# async def update_order(id: UUID, payload: schema.UpdateOrder, db: AsyncSession) -> schema.ReadOrder:
#     order = await get_order_by_id(id, db)

#     data = schema.UpdateOrder.model_dump(payload, exclude_unset=True)
#     for key, value in data.items():
#         setattr(order, key, value)

#     await db.commit()
#     return order

# async def delete_order(id: UUID, db: AsyncSession):
#     order = await get_order_by_id(id, db)
    
#     if order:       
#         await db.execute(delete(Order).where(Order.id == id))
#         await db.commit()
    

# async def count_order(db: AsyncSession) -> int:
#     result = await db.execute(select(func.count()).select_from(Order))
#     return result.scalar_one()


# # Additional functions
# def order_orm_to_dict(order: Order):
#     order_dict = order.__dict__
#     order_dict.pop('_sa_instance_state')
#     return order_dict
