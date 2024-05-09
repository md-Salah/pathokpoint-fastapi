from fastapi import APIRouter, status, Query, Response
from uuid import UUID

from app.config.database import Session
from app.controller.auth import AdminAccessToken
import app.controller.payment_gateway as service
import app.pydantic_schema.payment_gateway as schema

router = APIRouter(prefix='/payment_gateway')


@router.get('/id/{id}', response_model=schema.PaymentGatewayOut)
async def get_payment_gateway_by_id(id: UUID, db: Session):
    return await service.get_payment_gateway_by_id(id, db)


@router.get('/all', response_model=list[schema.PaymentGatewayOut])
async def get_all_payment_gateways(*, page: int = Query(1, ge=1),
                                   per_page: int = Query(10, ge=1, le=100),
                                   db: Session,  response: Response):
    payment_gateways = await service.get_all_payment_gateways(page, per_page, db)
    total_payment_gateways = await service.count_payment_gateway(db)

    response.headers['X-Total-Count'] = str(total_payment_gateways)
    response.headers['X-Total-Pages'] = str(-(-total_payment_gateways // per_page))
    response.headers['X-Current-Page'] = str(page)
    response.headers['X-Per-Page'] = str(per_page)

    return payment_gateways


@router.post('', response_model=schema.PaymentGatewayOut, status_code=status.HTTP_201_CREATED)
async def create_payment_gateway(payload: schema.CreatePaymentGateway, _: AdminAccessToken, db: Session):
    return await service.create_payment_gateway(payload.model_dump(), db)


@router.patch('/{id}', response_model=schema.PaymentGatewayOut)
async def update_payment_gateway(id: UUID, payload: schema.UpdatePaymentGateway, _: AdminAccessToken, db: Session):
    return await service.update_payment_gateway(id, payload.model_dump(exclude_unset=True), db)


@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_payment_gateway(id: UUID, _: AdminAccessToken, db: Session):
    await service.delete_payment_gateway(id, db)
