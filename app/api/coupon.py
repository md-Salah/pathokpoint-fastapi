from fastapi import APIRouter, status, Query, Response
from uuid import UUID
from fastapi_filter import FilterDepends

from app.filter_schema.coupon import CouponFilter
from app.config.database import Session
import app.controller.coupon as coupon_service
import app.pydantic_schema.coupon as coupon_schema
from app.controller.auth import AdminAccessToken

router = APIRouter(prefix='/coupon')


@router.get('/id/{id}', response_model=coupon_schema.CouponOut)
async def get_coupon_by_id(id: UUID, db: Session):
    return await coupon_service.get_coupon_by_id(id, db)


@router.get('/all', response_model=list[coupon_schema.CouponOut])
async def get_all_coupons(*, page: int = Query(1, ge=1),
                          per_page: int = Query(10, ge=1, le=100),
                          filter: CouponFilter = FilterDepends(CouponFilter),
                          db: Session,  response: Response):
    coupons = await coupon_service.get_all_coupons(filter, page, per_page, db)
    total_coupons = await coupon_service.count_coupon(filter, db)

    response.headers['X-Total-Count'] = str(total_coupons)
    response.headers['X-Total-Pages'] = str(-(-total_coupons // per_page))
    response.headers['X-Current-Page'] = str(page)
    response.headers['X-Per-Page'] = str(per_page)

    return coupons


@router.post('', response_model=coupon_schema.CouponOut, status_code=status.HTTP_201_CREATED)
async def create_coupon(payload: coupon_schema.CreateCoupon, _: AdminAccessToken, db: Session):
    return await coupon_service.create_coupon(payload.model_dump(), db)


@router.patch('/{id}', response_model=coupon_schema.CouponOut)
async def update_coupon(id: UUID, payload: coupon_schema.UpdateCoupon, _: AdminAccessToken, db: Session):
    return await coupon_service.update_coupon(id, payload.model_dump(exclude_unset=True), db)


@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_coupon(id: UUID, _: AdminAccessToken, db: Session):
    await coupon_service.delete_coupon(id, db)
