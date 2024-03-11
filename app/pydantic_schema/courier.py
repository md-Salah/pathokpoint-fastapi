from pydantic import ConfigDict, NonNegativeFloat, Field

from app.constant.city import City
from app.constant.country import Country
from app.pydantic_schema.mixins import TimestampMixin, timestamp_mixin_example
from app.pydantic_schema.base import BaseModel

example_courier = {
    'method_name': 'Delivery Tiger - Inside Dhaka',
    'company_name': 'Delivery Tiger',
    'base_charge': 60,
    'weight_charge_per_kg': 20,
    'allow_cash_on_delivery': True,

    'include_country': [Country.BD],
    'include_city': [City.dhaka],
    'exclude_city': [],
}


class CourierBase(BaseModel):
    method_name: str
    company_name: str
    base_charge: NonNegativeFloat = Field(le=10000)
    weight_charge_per_kg: NonNegativeFloat = Field(0, le=1000)
    allow_cash_on_delivery: bool = True

    include_country: list[Country] = []
    include_city: list[City] = []
    exclude_city: list[City] = []

    model_config = ConfigDict(json_schema_extra={"example": example_courier})


class CreateCourier(CourierBase):
    pass


class UpdateCourier(CourierBase):
    method_name: str | None = None
    company_name: str | None = None
    base_charge: NonNegativeFloat | None = None
    weight_charge_per_kg: NonNegativeFloat | None = None
    allow_cash_on_delivery: bool | None = None


class CourierOut(CourierBase, TimestampMixin):
    model_config = ConfigDict(json_schema_extra={"example":
                                                 example_courier | timestamp_mixin_example})