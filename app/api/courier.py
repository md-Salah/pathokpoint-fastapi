from fastapi import APIRouter, Depends, status, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.config.database import get_db
import app.controller.courier as courier_service
import app.pydantic_schema.courier as courier_schema

router = APIRouter()


# Permission: Customer
@router.get('/courier/id/{id}', response_model=courier_schema.CourierOut)
async def get_courier_by_id(id: UUID, db: AsyncSession = Depends(get_db)):
    courier = await courier_service.get_courier_by_id(id, db)
    return courier_schema.CourierOut.model_validate(courier)


# Permission: Customer
@router.get('/couriers', response_model=list[courier_schema.CourierOut])
async def get_all_couriers(*, page: int = Query(1, ge=1),
                           per_page: int = Query(10, ge=1, le=100),
                           db: AsyncSession = Depends(get_db),  response: Response):
    couriers = await courier_service.get_all_couriers(page, per_page, db)
    total_couriers = await courier_service.count_courier(db)

    response.headers['X-Total-Count'] = str(total_couriers)
    response.headers['X-Total-Pages'] = str(-(-total_couriers // per_page))
    response.headers['X-Current-Page'] = str(page)
    response.headers['X-Per-Page'] = str(per_page)

    return [courier_schema.CourierOut.model_validate(courier) for courier in couriers]


# Permission: Admin
@router.post('/courier', response_model=courier_schema.CourierOut, status_code=status.HTTP_201_CREATED)
async def create_courier(payload: courier_schema.CreateCourier, db: AsyncSession = Depends(get_db)):
    courier = await courier_service.create_courier(payload.model_dump(), db)
    return courier_schema.CourierOut.model_validate(courier)


# Permission: Admin
@router.patch('/courier/{id}', response_model=courier_schema.CourierOut)
async def update_courier(id: UUID, payload: courier_schema.UpdateCourier, db: AsyncSession = Depends(get_db)):
    courier = await courier_service.update_courier(id, payload.model_dump(exclude_unset=True), db)
    return courier_schema.CourierOut.model_validate(courier)


# Permission: Admin
@router.delete('/courier/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_courier(id: UUID, db: AsyncSession = Depends(get_db)):
    await courier_service.delete_courier(id, db)
