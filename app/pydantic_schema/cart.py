
from pydantic import ConfigDict, Field, NonNegativeFloat, FiniteFloat
from typing import List

from app.pydantic_schema.base import BaseModel
from app.pydantic_schema.order_item import ItemIn

example_apply_coupon = {
    "coupon_code": "welcome23",
    "order_items": [
        ItemIn._example,
    ]
}


class ApplyCoupon(BaseModel):
    coupon_code: str = Field(min_length=3, max_length=20)
    order_items: List[ItemIn]

    model_config = ConfigDict(
        json_schema_extra={"example": example_apply_coupon})


class ApplyCouponResponse(BaseModel):
    discount: NonNegativeFloat
    shipping_charge: FiniteFloat
