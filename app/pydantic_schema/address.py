from pydantic import ConfigDict, Field, UUID4

from app.constant.city import City
from app.constant.country import Country
from app.pydantic_schema.mixins import TimestampMixin, timestamp_mixin_example
from app.pydantic_schema.base import BaseModel

example_address = {
    'phone_number': '+8801511112222',
    'alternative_phone_number': '+8801633334444',
    'address': 'House 1, Road 1, Block A, Dhaka',
    'thana': 'dhanmondi',
    'city': City.dhaka,
    'country': Country.BD,
}

relationship_out = {
    'user_id': 'f5d3b3e3-3e0e-4f3e-8e3e-3e3e3e3e3e3e',
}


class AddressBase(BaseModel):
    phone_number: str | None = Field(None, min_length=14, max_length=14)
    alternative_phone_number: str | None = Field(None, min_length=14, max_length=14)
    address: str = Field(min_length=5, max_length=500)
    thana: str = Field(min_length=3, max_length=50)
    city: City
    country: Country

    model_config = ConfigDict(json_schema_extra={"example": example_address})


class CreateAddress(AddressBase):
    pass


class UpdateAddress(AddressBase):
    address: str | None = Field(None, min_length=3, max_length=500)
    thana: str | None = Field(None, min_length=3, max_length=50)
    city: City | None = None
    country: Country | None = None


class AddressOut(AddressBase, TimestampMixin):
    user_id: UUID4
    model_config = ConfigDict(json_schema_extra={"example":
                                                 example_address | relationship_out | timestamp_mixin_example})
