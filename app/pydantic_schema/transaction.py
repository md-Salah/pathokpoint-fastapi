from pydantic import ConfigDict, Field, UUID4

from app.pydantic_schema.mixins import IdTimestampMixin
from app.pydantic_schema.base import BaseModel
from app.pydantic_schema.common import OrderOut, UserOut, PaymentGatewayOut

example_transaction = {
    'amount': 100,
    'transaction_id': 'UEIS78D9D',
    'reference': 'abdul kuddus',
    'account_number': '+8801534567890',
}

example_transaction_in = {
    'payment_method': 'bkash',
    **example_transaction,
}

example_refund_transaction_in = {
    **example_transaction_in,
    'refund_reason': 'order cancelled',
    'order_id': 'valid-uuid4',
}

example_transaction_out = {
    **IdTimestampMixin._example,
    **example_refund_transaction_in,
    'gateway': PaymentGatewayOut._example,
    'order': OrderOut._example,
    'customer': UserOut._example,
    'is_manual': False,
    'refunded_by': UserOut._example,
    'is_refund': True,
}


class TransactionBase(BaseModel):
    amount: float = Field(..., gt=0, le=10000)
    transaction_id: str = Field(..., min_length=3, max_length=100)
    reference: str | None = Field(None, max_length=100)
    account_number: str = Field(..., min_length=3, max_length=17)


class CreateTransaction(TransactionBase):
    payment_method: str
    model_config = ConfigDict(
        json_schema_extra={"example": example_transaction_in})


class CreateRefundTransaction(CreateTransaction):
    order_id: UUID4
    refund_reason: str | None = Field(None, min_length=3, max_length=100)

    model_config = ConfigDict(
        json_schema_extra={"example": example_refund_transaction_in})


class TransactionOut(TransactionBase, IdTimestampMixin):
    gateway: PaymentGatewayOut
    order: OrderOut
    customer: UserOut | None
    is_manual: bool
    refunded_by: UserOut | None
    is_refund: bool
    refund_reason: str | None

    model_config = ConfigDict(json_schema_extra={"example":
                                                 example_transaction_out})
