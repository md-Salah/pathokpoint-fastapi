from pydantic import ConfigDict, Field, UUID4

from app.constant.city import City
from app.constant.country import Country
from app.pydantic_schema.mixins import IdTimestampMixin
from app.pydantic_schema.base import BaseModel

example_address = {
    'phone_number': '+8801511112222',
    'alternative_phone_number': '+8801633334444',
    'address': 'House 1, Road 1, Block A, Dhaka',
    'thana': 'dhanmondi',
    'city': City.dhaka,
    'country': Country.BD,
}

example_address_in = {
    **example_address,
}

example_address_out = {
    **example_address,
    **IdTimestampMixin._example,
    'user_id': 'example-uuid',
}


class AddressBase(BaseModel):
    phone_number: str | None = Field(None, min_length=14, max_length=14)
    alternative_phone_number: str | None = Field(
        None, min_length=14, max_length=14)
    address: str = Field(min_length=5, max_length=500)
    thana: str = Field(min_length=3, max_length=50)
    city: City
    country: Country


class CreateAddress(AddressBase):
    model_config = ConfigDict(
        json_schema_extra={"example": example_address_in})


class UpdateAddress(AddressBase):
    address: str | None = Field(None, min_length=3, max_length=500)
    thana: str | None = Field(None, min_length=3, max_length=50)
    city: City | None = None
    country: Country | None = None


class AddressOut(AddressBase, IdTimestampMixin):
    user_id: UUID4
    model_config = ConfigDict(json_schema_extra={"example":
                                                 example_address_out})
