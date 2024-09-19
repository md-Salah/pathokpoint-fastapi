from fastapi import APIRouter, Query, Request, BackgroundTasks
from fastapi.responses import RedirectResponse
import logging
import traceback

import app.controller.payment as service
from app.config.settings import settings
from app.config.database import Session

router = APIRouter(prefix='/payment')
logger = logging.getLogger(__name__)


@router.get('/bkash/callback')
async def pay_with_bkash_callback(*, payment_id: str = Query(alias="paymentID"),
                                  status: str = Query(),
                                  signature: str = Query(), bg_task: BackgroundTasks, request: Request, db: Session):

    try:
        order = await service.execute_payment(payment_id, status, request, bg_task, db)
        if order:
            return RedirectResponse(f'{settings.FRONTEND_URL}/checkout/success?invoice={order.invoice}&id={order.id}')
        else:
            return RedirectResponse(f'{settings.FRONTEND_URL}/checkout/failed')
    except Exception:
        logger.error(traceback.format_exc())
        return RedirectResponse(f'{settings.FRONTEND_URL}/checkout/failed')
        