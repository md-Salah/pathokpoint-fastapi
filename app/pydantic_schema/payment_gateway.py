from pydantic import ConfigDict, Field
from app.pydantic_schema.mixins import TimestampMixin, timestamp_mixin_example
from app.pydantic_schema.base import BaseModel


example_payment_gateway = {
    'name': 'bKash',
    'description': 'bKash Payment Gateway',
    'is_enabled': True,
}

class PaymentGatewayBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: str | None = Field(None, min_length=3, max_length=100)
    is_enabled: bool = True

    model_config = ConfigDict(json_schema_extra={"example": example_payment_gateway})

class CreatePaymentGateway(PaymentGatewayBase):
    pass

class UpdatePaymentGateway(CreatePaymentGateway):
    name: str | None = Field(None, min_length=3, max_length=100)

class PaymentGatewayOut(PaymentGatewayBase, TimestampMixin):
    model_config = ConfigDict(json_schema_extra={"example":
                                                 example_payment_gateway | timestamp_mixin_example})
