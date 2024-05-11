from pydantic import ConfigDict, Field, UUID4

from app.constant.city import City
from app.constant.country import Country
from app.pydantic_schema.mixins import IdTimestampMixin
from app.pydantic_schema.base import BaseModel
from app.pydantic_schema.field import PhoneNumberField

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
    **example_address_in,
    **IdTimestampMixin._example,
    'user_id': 'valid-uuid',
}


class AddressBase(BaseModel):
    phone_number: str = PhoneNumberField()
    alternative_phone_number: str = PhoneNumberField(None)
    address: str = Field(min_length=5, max_length=500)
    thana: str = Field(min_length=3, max_length=50)
    city: City
    country: Country


class CreateAddress(AddressBase):
    model_config = ConfigDict(
        json_schema_extra={"example": example_address_in})


class UpdateAddress(CreateAddress):
    phone_number: str = PhoneNumberField(None)
    address: str = Field(None, min_length=3, max_length=500)
    thana: str = Field(None, min_length=3, max_length=50)
    city: City = Field(None)
    country: Country = Field(None)


class AddressOut(CreateAddress, IdTimestampMixin):
    user_id: UUID4
    model_config = ConfigDict(json_schema_extra={"example":
                                                 example_address_out})
