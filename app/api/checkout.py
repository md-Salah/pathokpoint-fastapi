from fastapi import APIRouter

import app.pydantic_schema.order as order_schema
import app.pydantic_schema.checkout as schema
from app.config.database import Session
import app.controller.checkout as service


router = APIRouter(prefix='/checkout')


@router.post('/summary', response_model=schema.CheckoutSummary)
async def checkout_summary(payload: order_schema.CreateOrder, db: Session):
    return await service.checkout_summary(payload.model_dump(), db)
