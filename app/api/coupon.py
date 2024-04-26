from fastapi import APIRouter, Depends, status, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.config.database import get_db
import app.controller.coupon as coupon_service
import app.pydantic_schema.coupon as coupon_schema

router = APIRouter()


@router.get('/coupon/id/{id}', response_model=coupon_schema.CouponOut)
async def get_coupon_by_id(id: UUID, db: AsyncSession = Depends(get_db)):
    return await coupon_service.get_coupon_by_id(id, db)

@router.get('/coupon/admin/id/{id}', response_model=coupon_schema.CouponOutAdmin)
async def get_coupon_by_id_admin(id: UUID, db: AsyncSession = Depends(get_db)):
    return await coupon_service.get_coupon_by_id(id, db)


@router.get('/coupons', response_model=list[coupon_schema.CouponOut])
async def get_all_coupons(*, page: int = Query(1, ge=1),
                          per_page: int = Query(10, ge=1, le=100),
                          db: AsyncSession = Depends(get_db),  response: Response):
    coupons = await coupon_service.get_all_coupons(page, per_page, db)
    total_coupons = await coupon_service.count_coupon(db)

    response.headers['X-Total-Count'] = str(total_coupons)
    response.headers['X-Total-Pages'] = str(-(-total_coupons // per_page))
    response.headers['X-Current-Page'] = str(page)
    response.headers['X-Per-Page'] = str(per_page)

    return coupons


@router.post('/coupon', response_model=coupon_schema.CouponOut, status_code=status.HTTP_201_CREATED)
async def create_coupon(payload: coupon_schema.CreateCoupon, db: AsyncSession = Depends(get_db)):
    return await coupon_service.create_coupon(payload.model_dump(), db)


@router.patch('/coupon/{id}', response_model=coupon_schema.CouponOut)
async def update_coupon(id: UUID, payload: coupon_schema.UpdateCoupon, db: AsyncSession = Depends(get_db)):
    return await coupon_service.update_coupon(id, payload.model_dump(exclude_unset=True), db)


@router.delete('/coupon/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_coupon(id: UUID, db: AsyncSession = Depends(get_db)):
    await coupon_service.delete_coupon(id, db)
