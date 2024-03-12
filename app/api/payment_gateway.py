from fastapi import APIRouter, Depends, status, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.config.database import get_db
import app.controller.payment_gateway as payment_gateway_service
import app.pydantic_schema.payment_gateway as payment_gateway_schema

router = APIRouter()


@router.get('/payment_gateway/id/{id}', response_model=payment_gateway_schema.PaymentGatewayOut)
async def get_payment_gateway_by_id(id: UUID, db: AsyncSession = Depends(get_db)):
    payment_gateway = await payment_gateway_service.get_payment_gateway_by_id(id, db)
    return payment_gateway_schema.PaymentGatewayOut.model_validate(payment_gateway)


@router.get('/payment_gateways', response_model=list[payment_gateway_schema.PaymentGatewayOut])
async def get_all_payment_gateways(*, page: int = Query(1, ge=1),
                                   per_page: int = Query(10, ge=1, le=100),
                                   db: AsyncSession = Depends(get_db),  response: Response):
    payment_gateways = await payment_gateway_service.get_all_payment_gateways(page, per_page, db)
    total_payment_gateways = await payment_gateway_service.count_payment_gateway(db)

    response.headers['X-Total-Count'] = str(total_payment_gateways)
    response.headers['X-Total-Pages'] = str(-(-total_payment_gateways // per_page))
    response.headers['X-Current-Page'] = str(page)
    response.headers['X-Per-Page'] = str(per_page)

    return [payment_gateway_schema.PaymentGatewayOut.model_validate(payment_gateway) for payment_gateway in payment_gateways]


@router.post('/payment_gateway', response_model=payment_gateway_schema.PaymentGatewayOut, status_code=status.HTTP_201_CREATED)
async def create_payment_gateway(payload: payment_gateway_schema.CreatePaymentGateway, db: AsyncSession = Depends(get_db)):
    payment_gateway = await payment_gateway_service.create_payment_gateway(payload.model_dump(), db)
    return payment_gateway_schema.PaymentGatewayOut.model_validate(payment_gateway)


@router.patch('/payment_gateway/{id}', response_model=payment_gateway_schema.PaymentGatewayOut)
async def update_payment_gateway(id: UUID, payload: payment_gateway_schema.UpdatePaymentGateway, db: AsyncSession = Depends(get_db)):
    payment_gateway = await payment_gateway_service.update_payment_gateway(id, payload.model_dump(exclude_unset=True), db)
    return payment_gateway_schema.PaymentGatewayOut.model_validate(payment_gateway)


@router.delete('/payment_gateway/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_payment_gateway(id: UUID, db: AsyncSession = Depends(get_db)):
    await payment_gateway_service.delete_payment_gateway(id, db)
