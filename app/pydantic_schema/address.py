from pydantic import ConfigDict, Field, UUID4

from app.constant.city import City
from app.constant.country import Country
from app.pydantic_schema.mixins import TimestampMixin, timestamp_mixin_example
from app.pydantic_schema.base import BaseModel

example_address = {
    'phone_number': '01710000000',
    'alternative_phone_number': '01710000001',
    'address': 'House 1, Road 1, Block A, Dhaka',
    'thana': 'dhanmondi',
    'city': City.dhaka,
    'country': Country.bangladesh,
}


class AddressBase(BaseModel):
    phone_number: str | None = Field(min_length=11, max_length=14, default=None)
    alternative_phone_number: str | None = Field(min_length=11, max_length=14, default=None)
    address: str = Field(min_length=5, max_length=500)
    thana: str = Field(min_length=3, max_length=50)
    city: City = Field(min_length=3, max_length=50)
    country: Country = Field(min_length=3, max_length=50, default=Country.bangladesh)

    model_config = ConfigDict(json_schema_extra={"example": example_address})


class CreateAddress(AddressBase):
    pass


class UpdateAddress(AddressBase):
    address: str | None = Field(min_length=3, max_length=500, default=None)
    thana: str | None = Field(min_length=3, max_length=50, default=None)
    city: City | None = Field(min_length=3, max_length=50, default=None)
    country: Country | None = Field(min_length=3, max_length=50, default=None)


class AddressOut(AddressBase, TimestampMixin):
    user_id: UUID4
    model_config = ConfigDict(json_schema_extra={"example":
                                                 example_address | timestamp_mixin_example})
