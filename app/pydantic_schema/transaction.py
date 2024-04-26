from pydantic import ConfigDict, Field, UUID4, root_validator

from app.pydantic_schema.mixins import IdTimestampMixin
from app.pydantic_schema.base import BaseModel
from app.pydantic_schema.common import OrderOut, UserOut, PaymentGatewayOut

example_transaction = {
    'amount': 100,
    'transaction_id': 'UEIS78D9D',
    'reference': 'abdul kuddus',
    'account_number': '+8801534567890',
    'is_manual': False,
}

example_transaction_in = {
    **example_transaction,
    'gateway_id': 'valid-uuid4',
    'order_id': 'valid-uuid4',
}

example_refund_transaction_in = {
    **example_transaction_in,
    'is_refund': True,
    'refund_reason': 'order cancelled',
    'refunded_by_id': 'valid-uuid4'
}

example_transaction_out = {
    **example_transaction,
    **IdTimestampMixin._example,
    'gateway': PaymentGatewayOut._example,
    'order': OrderOut._example,
    'refunded_by': UserOut._example,
}


class TransactionBase(BaseModel):
    amount: float = Field(..., gt=0, le=10000)
    transaction_id: str = Field(..., min_length=3, max_length=100)
    reference: str | None = Field(None, min_length=3, max_length=100)
    account_number: str = Field(..., min_length=3, max_length=17)
    is_manual: bool = False


class CreateTransaction(TransactionBase):
    gateway_id: UUID4
    order_id: UUID4 | None = None

    model_config = ConfigDict(
        json_schema_extra={"example": example_transaction_in})


class RefundTransactionBase(TransactionBase):
    is_refund: bool = True
    refund_reason: str | None = Field(None, min_length=3, max_length=100)


class CreateRefundTransaction(CreateTransaction, RefundTransactionBase):
    refunded_by_id: UUID4

    model_config = ConfigDict(
        json_schema_extra={"example": example_refund_transaction_in})


class TransactionOut(RefundTransactionBase, IdTimestampMixin):
    gateway: PaymentGatewayOut
    order: OrderOut | None = None
    refunded_by: UserOut | None = None

    model_config = ConfigDict(json_schema_extra={"example":
                                                 example_transaction_out})
