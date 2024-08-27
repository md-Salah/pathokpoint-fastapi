
from pydantic import ConfigDict, NonNegativeFloat, ValidationInfo, field_validator, UUID4
from app.pydantic_schema.base import BaseModel
from app.pydantic_schema.order import OrderBase

class CheckoutSummaryIn(OrderBase):
    @field_validator('address_id')
    @classmethod
    def validate_address_is_required(cls, v: UUID4 | None, info: ValidationInfo):
        if v is None and info.data['address'] is None:
            raise ValueError('Either address or address_id is required')
        return v

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
