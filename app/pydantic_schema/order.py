from pydantic import UUID4, ConfigDict, Field, NonNegativeFloat, FiniteFloat, ValidationInfo, field_validator
from typing import List

from app.pydantic_schema.base import BaseModel
from app.pydantic_schema.mixins import IdTimestampMixin
from app.pydantic_schema.common import UserOut, CouponOut, CourierOut
from app.pydantic_schema.transaction import TransactionOut, CreateTransaction, example_transaction_in
from app.pydantic_schema.address import AddressOut, CreateAddress, example_address_in
from app.pydantic_schema.order_item import ItemIn, ItemOut, ItemUpdate
from app.pydantic_schema.order_status import StatusIn, StatusOut

example_order_base = {
    'order_items': [ItemIn._example],
    'coupon_code': 'Welcome10',
    'is_full_paid': True,
    'address': example_address_in,
    'address_id': 'valid-uuid4',
    'courier_id': 'valid-uuid4',
    'customer_note': 'Please deliver fast',
}

example_order_in = {
    **example_order_base,
    'payment_method': 'bkash',
}

example_order_update_admin = {
    'order_items': [ItemUpdate._example],
    'discount': 100,
    'tracking_id': 'DT-546365',
    'shipping_cost': 120,
    'cod_received': 530,
    'cost_of_good_new': 50,
    'additional_cost': 10,
    'order_status': StatusIn._example,
    "transaction": example_transaction_in,
}

example_order_out = {
    **IdTimestampMixin._example,
    **example_order_in,
    'invoice': 1,
    'order_items': [ItemOut._example],
    'new_book_total': 400,
    'old_book_total': 100,
    'shipping_charge': 100,
    'weight_charge': 0,
    'total': 600,
    'discount': 100,
    'net_amount': 500,
    'paid': 500,
    'due': 0,
    'refunded': 0,
    'tracking_id': 'DT-546365',
    'order_status': [StatusOut._example],
    'transactions': [TransactionOut._example],
    'coupon': CouponOut._example,
    'customer': UserOut._example,
    'address': AddressOut._example,
    'courier': CourierOut._example,
}

example_order_out_admin = {
    **example_order_out,
    'shipping_cost': 60,
    'cod_receivable': 530,
    'cod_received': 530,
    'cost_of_good_new': 0,
    'cost_of_good_old': 400,
    'additional_cost': 10,
    'gross_profit': 120,
}


class OrderBase(BaseModel):
    order_items: List[ItemIn]
    coupon_code: str | None = None
    is_full_paid: bool = True
    address: CreateAddress | None = None
    address_id: UUID4 | None = None
    courier_id: UUID4
    customer_note: str | None = None


class CreateOrder(OrderBase):
    payment_method: str

    model_config = ConfigDict(json_schema_extra={"example": example_order_in})

    @field_validator('address_id')
    @classmethod
    def validate_address_is_required(cls, v: UUID4 | None, info: ValidationInfo):
        if v is None and info.data['address'] is None:
            raise ValueError('Either address or address_id is required')
        return v


class CreateOrderAdmin(OrderBase):
    courier_id: UUID4 | None = None
    customer_id: UUID4 | None = None
    transactions: List[CreateTransaction] = []

    model_config = ConfigDict(json_schema_extra={"example": {
        **example_order_in,
        'customer_id': 'valid-uuid4',
        'transactions': [example_transaction_in]
    }})


class OrderOut(OrderBase, IdTimestampMixin):
    invoice: int
    order_items: List[ItemOut]
    new_book_total: NonNegativeFloat
    old_book_total: NonNegativeFloat
    shipping_charge: NonNegativeFloat
    weight_charge: NonNegativeFloat
    total: NonNegativeFloat
    discount: NonNegativeFloat
    net_amount: NonNegativeFloat
    paid: NonNegativeFloat
    due: FiniteFloat
    refunded: NonNegativeFloat

    tracking_id: str | None

    order_status: List[StatusOut]
    transactions: List[TransactionOut] = []
    coupon: CouponOut | None = None
    customer: UserOut | None = None
    address: AddressOut | None = None
    courier: CourierOut | None = None
    courier_id: UUID4 | None = None

    model_config = ConfigDict(json_schema_extra={"example": example_order_out})


class UpdateOrderAdmin(BaseModel):
    order_items: List[ItemUpdate] = []
    discount: NonNegativeFloat = 0
    tracking_id: str | None = None
    shipping_cost: NonNegativeFloat = 0
    cod_received: NonNegativeFloat = 0
    cost_of_good_new: NonNegativeFloat = 0
    additional_cost: NonNegativeFloat = 0
    order_status: StatusIn = Field(None)
    transaction: CreateTransaction | None = None

    model_config = ConfigDict(
        json_schema_extra={"example": example_order_update_admin})


class OrderOutAdmin(OrderOut):
    courier_id: UUID4 | None = None
    shipping_cost: NonNegativeFloat
    cod_receivable: NonNegativeFloat
    cod_received: NonNegativeFloat
    cost_of_good_new: NonNegativeFloat
    cost_of_good_old: NonNegativeFloat
    additional_cost: NonNegativeFloat
    gross_profit: FiniteFloat

    model_config = ConfigDict(
        json_schema_extra={"example": example_order_out_admin})
