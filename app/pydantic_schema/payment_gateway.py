from pydantic import ConfigDict, Field
from app.pydantic_schema.mixins import IdTimestampMixin
from app.pydantic_schema.base import BaseModel
from app.pydantic_schema.common import ImageOut

example_payment_gateway = {
    'name': 'bkash',
    'title': 'bKash',
    'is_disabled': False,
    'is_admin_only': False,
}

example_payment_gateway_in = {
    **example_payment_gateway,
}

example_payment_gateway_out = {
    **IdTimestampMixin._example,
    **example_payment_gateway,
    'image': ImageOut._example,
}


class PaymentGatewayBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=20)
    title: str = Field(..., min_length=3, max_length=20)
    is_disabled: bool = False
    is_admin_only: bool = False


class CreatePaymentGateway(PaymentGatewayBase):
    model_config = ConfigDict(
        json_schema_extra={"example": example_payment_gateway_in})


class UpdatePaymentGateway(CreatePaymentGateway):
    name: str = Field(None, min_length=3, max_length=20)
    title: str = Field(None, min_length=3, max_length=20)


class PaymentGatewayOut(CreatePaymentGateway, IdTimestampMixin):
    image: ImageOut | None = None
    model_config = ConfigDict(json_schema_extra={"example":
                                                 example_payment_gateway_out})
