from fastapi import APIRouter

import app.pydantic_schema.checkout as schema
from app.config.database import Session
import app.controller.checkout as service
from app.controller.auth import AccessTokenOptional

router = APIRouter(prefix='/checkout')


@router.post('/summary', response_model=schema.CheckoutSummary)
async def checkout_summary(payload: schema.CheckoutSummaryIn, token: AccessTokenOptional, db: Session):
    data = payload.model_dump()
    if token:
        data['customer_id'] = token['id']
    return await service.checkout_summary(data, db)
