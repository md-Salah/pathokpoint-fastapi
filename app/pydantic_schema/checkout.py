
from pydantic import ConfigDict, NonNegativeFloat
from app.pydantic_schema.base import BaseModel


class CheckoutSummary(BaseModel):
    sub_total: NonNegativeFloat
    shipping_charge: NonNegativeFloat
    weight_charge: NonNegativeFloat
    discount: NonNegativeFloat
    coupon_code: str | None = None

    model_config = ConfigDict(
        json_schema_extra={"example": {
            'sub_total': 600,
            'shipping_charge': 60,
            'weight_charge': 20,
            'discount': 0,
            'coupon_code': 'welcome36'
        }})
