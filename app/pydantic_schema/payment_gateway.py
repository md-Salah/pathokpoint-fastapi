from pydantic import ConfigDict, Field
from app.pydantic_schema.mixins import IdTimestampMixin
from app.pydantic_schema.base import BaseModel


example_payment_gateway = {
    'name': 'bKash',
    'description': 'bKash Payment Gateway',
    'is_enabled': True,
}

example_payment_gateway_in = {
    **example_payment_gateway,
}

example_payment_gateway_out = {
    **IdTimestampMixin._example,
    **example_payment_gateway,
}


class PaymentGatewayBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=20)
    description: str | None = Field(None, min_length=3, max_length=100)
    is_enabled: bool = True


class CreatePaymentGateway(PaymentGatewayBase):
    model_config = ConfigDict(
        json_schema_extra={"example": example_payment_gateway_in})


class UpdatePaymentGateway(CreatePaymentGateway):
    name: str = Field(None, min_length=3, max_length=20)


class PaymentGatewayOut(CreatePaymentGateway, IdTimestampMixin):
    model_config = ConfigDict(json_schema_extra={"example":
                                                 example_payment_gateway_out})
