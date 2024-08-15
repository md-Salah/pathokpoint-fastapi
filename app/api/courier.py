from fastapi import APIRouter, status, Query, Response
from uuid import UUID
from fastapi_filter import FilterDepends

from app.config.database import Session
from app.controller.auth import AdminAccessToken
import app.controller.courier as courier_service
import app.pydantic_schema.courier as courier_schema
from app.filter_schema.courier import CourierFilter

router = APIRouter(prefix='/courier')


@router.get('/id/{id}', response_model=courier_schema.CourierOut)
async def get_courier_by_id(id: UUID, db: Session):
    return await courier_service.get_courier_by_id(id, db)


@router.get('/all', response_model=list[courier_schema.CourierOut])
async def get_all_couriers(*,
                           filter: CourierFilter = FilterDepends(
                               CourierFilter),
                           page: int = Query(1, ge=1),
                           per_page: int = Query(10, ge=1, le=100),
                           db: Session,  response: Response):
    couriers = await courier_service.get_all_couriers(filter, page, per_page, db)
    total_couriers = await courier_service.count_courier(filter, db)

    response.headers['X-Total-Count'] = str(total_couriers)
    response.headers['X-Total-Pages'] = str(-(-total_couriers // per_page))
    response.headers['X-Current-Page'] = str(page)
    response.headers['X-Per-Page'] = str(per_page)

    return couriers


@router.post('', response_model=courier_schema.CourierOut, status_code=status.HTTP_201_CREATED)
async def create_courier(payload: courier_schema.CreateCourier, _: AdminAccessToken, db: Session):
    return await courier_service.create_courier(payload.model_dump(), db)


@router.patch('/{id}', response_model=courier_schema.CourierOut)
async def update_courier(id: UUID, payload: courier_schema.UpdateCourier, _: AdminAccessToken, db: Session):
    return await courier_service.update_courier(id, payload.model_dump(exclude_unset=True), db)


@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_courier(id: UUID, _: AdminAccessToken, db: Session):
    await courier_service.delete_courier(id, db)
