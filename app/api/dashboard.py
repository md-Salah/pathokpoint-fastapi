from datetime import datetime

from fastapi import APIRouter

import app.controller.dashboard as service
import app.pydantic_schema.dashboard as schema
from app.config.database import Session
from app.controller.auth import AdminAccessToken

router = APIRouter(prefix='/dashboard')


@router.get('/order', response_model=schema.OrderAnalysis)
async def get_order_analysis(*, from_date: datetime | None = None,
                             to_date: datetime | None = None,
                             _: AdminAccessToken,
                             db: Session) -> dict:
    return await service.order_analysis(from_date, to_date, db)


@router.get('/inventory', response_model=list[schema.ProductGroup])
async def get_inventory_analysis(*, _: AdminAccessToken, db: Session) -> list[dict]:
    return await service.inventory_analysis(db)
