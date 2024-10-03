import logging

from fastapi import APIRouter, BackgroundTasks, Query, Request
from fastapi.responses import RedirectResponse

import app.controller.payment as service
from app.config.database import Session
from app.config.settings import settings

router = APIRouter(prefix='/payment')
logger = logging.getLogger(__name__)


@router.get('/bkash/callback')
async def pay_with_bkash_callback(*, payment_id: str = Query(alias="paymentID"),
                                  status: str = Query(),
                                  signature: str = Query(), bg_task: BackgroundTasks, request: Request, db: Session):

    order = await service.execute_payment(payment_id, status, request, bg_task, db)
    if order:
        return RedirectResponse(f'{settings.FRONTEND_URL}/checkout/success?invoice={order.invoice}&id={order.id}')
    else:
        return RedirectResponse(f'{settings.FRONTEND_URL}/checkout/failed')
