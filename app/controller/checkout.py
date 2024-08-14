from sqlalchemy.ext.asyncio import AsyncSession
import logging
from typing import Any

import app.controller.order as order_service

logger = logging.getLogger(__name__)


async def checkout_summary(payload: dict[str, Any], db: AsyncSession):
    order = await order_service.create_order(payload, db, commit=False)
    return {
        'sub_total': order.old_book_total + order.new_book_total,
        'shipping_charge': order.shipping_charge,
        'weight_charge': order.weight_charge,
        'discount': order.discount,
        'coupon_code': payload.get('coupon_code')
    }
