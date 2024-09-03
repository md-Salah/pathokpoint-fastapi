from fastapi import APIRouter, Query, Request, BackgroundTasks
from fastapi.responses import RedirectResponse
from uuid import UUID

import app.controller.payment as service
import app.controller.email as email_service
from app.config.settings import settings
from app.config.database import Session

router = APIRouter(prefix='/payment')


@router.get('/bkash')
async def pay_with_bkash(*, order_id: UUID = Query(), request: Request, db: Session):
    callback_url = str(request.url_for('pay_with_bkash_callback'))
    return await service.pay_with_bkash(order_id, callback_url, db)


@router.get('/bkash/callback')
async def pay_with_bkash_callback(*, payment_id: str = Query(alias="paymentID"),
                                  status: str = Query(),
                                  signature: str = Query(), bg_task: BackgroundTasks, db: Session):
    if status == 'success':
        order = await service.execute_payment(payment_id, db)
        if order:
            if (await order.awaitable_attrs.address) and order.address.email:
                bg_task.add_task(email_service.payment_recieved_email, order)
            return RedirectResponse(f'{settings.FRONTEND_URL}/checkout/success?invoice={order.invoice}&id={order.id}')
        else:
            return RedirectResponse(f'{settings.FRONTEND_URL}/checkout/failed')
    else:
        return RedirectResponse(f'{settings.FRONTEND_URL}/checkout/failed')
