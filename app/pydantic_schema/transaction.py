from pydantic import ConfigDict, Field, UUID4

from app.pydantic_schema.mixins import TimestampMixin, timestamp_mixin_example
from app.pydantic_schema.base import BaseModel
from app.pydantic_schema.order import OrderOut
from app.pydantic_schema.user import UserOut
from app.pydantic_schema.payment_gateway import PaymentGatewayOut, example_payment_gateway

example_transaction = {
    'amount': 100,
    'transaction_id': 'UEIS78D9D',
    'reference': 'abdul kuddus',
    'account_number': '+8801534567890',
    'is_manual': False,
}

example_transaction_in = {
    **example_transaction,
    'gateway': '5b36385d-27bf-47dd-9126-df04bccfc773',
    'order': '5b36385d-27bf-47dd-9126-df04bccfc773',
}

example_refund_transaction_in = {
    **example_transaction_in,
    'is_refund': True,
    'refund_reason': 'order cancelled',
    'refunded_by': '5b36385d-27bf-47dd-9126-df04bccfc773'
}

example_transaction_out = {
    **example_transaction,
    'gateway': example_payment_gateway,
    'order': {},
    'refunded_by': {}
}


class TransactionBase(BaseModel):
    amount: float = Field(..., gt=0, le=10000)
    transaction_id: str = Field(..., min_length=3, max_length=100)
    reference: str | None = Field(None, min_length=3, max_length=100)
    account_number: str = Field(..., min_length=3, max_length=17)
    is_manual: bool = False
    
class RefundTransactionBase(TransactionBase):
    is_refund: bool = True
    refund_reason: str | None = Field(None, min_length=3, max_length=100)

class CreateTransaction(TransactionBase):
    gateway: UUID4
    order: UUID4 | None = None
    
    model_config = ConfigDict(json_schema_extra={"example": example_transaction_in})

class CreateRefundTransaction(CreateTransaction, RefundTransactionBase):
    refunded_by: UUID4
    
    model_config = ConfigDict(json_schema_extra={"example": example_refund_transaction_in})

class TransactionOut(RefundTransactionBase, TimestampMixin):
    gateway: PaymentGatewayOut
    order: OrderOut | None = None
    refunded_by: UserOut | None = None
        
    model_config = ConfigDict(json_schema_extra={"example":
                                                 example_transaction_out | timestamp_mixin_example})
