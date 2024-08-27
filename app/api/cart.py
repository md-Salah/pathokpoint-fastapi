from fastapi import APIRouter, Query

import app.pydantic_schema.cart as schema
import app.pydantic_schema.coupon as coupon_schema
from app.config.database import Session
import app.controller.cart as cart_service
import app.controller.coupon as coupon_service
from app.controller.auth import AccessTokenOptional


router = APIRouter(prefix='/cart')


@router.post('/apply-coupon', response_model=schema.ApplyCouponResponse)
async def apply_coupon(payload: schema.ApplyCoupon, token: AccessTokenOptional, db: Session):
    payload.customer_id = token['id'] if token else None
    return await cart_service.apply_coupon(payload.model_dump(), db)


@router.get('/suggested-coupons', response_model=list[coupon_schema.CouponOut])
async def get_suggested_coupons(*, page: int = Query(1, ge=1),
                                per_page: int = Query(10, ge=1, le=100),
                                db: Session):
    return await coupon_service.get_suggested_coupons(page, per_page, db)


@router.post('/verify-stock')
async def verify_stock(payload: schema.VerifyStock, db: Session):
    return await cart_service.verify_stock(payload.model_dump(), db)