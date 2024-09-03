from fastapi import APIRouter

import app.controller.email as service
from app.config.database import Session
from app.controller.auth import AdminAccessToken

router = APIRouter(prefix='/email')


@router.get('/test/invoice')
async def get_invoice(_: AdminAccessToken, email: str, db: Session):
    return await service.test_send_invoice_email(email, db)
