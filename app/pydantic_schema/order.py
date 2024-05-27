from pydantic import UUID4, ConfigDict, Field, NonNegativeFloat, FiniteFloat
from typing import List

from app.pydantic_schema.base import BaseModel
from app.pydantic_schema.mixins import IdTimestampMixin
from app.pydantic_schema.common import UserOut, CouponOut, CourierOut
from app.pydantic_schema.transaction import TransactionOut
from app.pydantic_schema.address import AddressOut
from app.pydantic_schema.order_item import ItemIn, ItemOut, ItemUpdate
from app.pydantic_schema.order_status import StatusIn, StatusOut

example_order_base = {
    'is_full_paid': True,
    'order_items': [ItemIn._example],
    'customer_note': 'Valo boi diben',
}

example_order_in = {
    **example_order_base,
    'coupon_id': 'valid-uuid4',
    'address_id': 'valid-uuid4',
    'courier_id': 'valid-uuid4',
}

example_order_update_admin = {
    'order_items': [ItemUpdate._example],
    'shipping_charge': 100,
    'weight_charge': 0,
    'discount': 100,
    'tracking_id': 'DT-546365',
    'shipping_cost': 120,
    'cod_receivable': 530,
    'cod_received': 530,
    'cost_of_good_new': 50,
    'cost_of_good_old': 400,
    'additional_cost': 10,
    'in_trash': False,
    'order_status': StatusIn._example,
    "transaction_id": "valid-uuid4"
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
    'payment_reversed': 0,
    'due': 0,
    'refunded': 0,
    'tracking_id': 'DT-546365',
    'order_status': [StatusOut._example],
    'transactions': [TransactionOut._example],
    'coupon': CouponOut._example,
    'customer': UserOut._example,
    'address': AddressOut._example,
    'courier': CourierOut._example,
    'in_trash': False,
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
    is_full_paid: bool = True
    order_items: List[ItemIn]
    customer_note: str | None = None


class CreateOrder(OrderBase):
    coupon_id: UUID4 | None = None
    address_id: UUID4
    courier_id: UUID4

    model_config = ConfigDict(json_schema_extra={"example": example_order_in})


class OrderOut(CreateOrder, IdTimestampMixin):
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
    payment_reversed: NonNegativeFloat
    due: FiniteFloat
    refunded: NonNegativeFloat

    tracking_id: str | None

    order_status: List[StatusOut]
    transactions: List[TransactionOut] = []
    coupon: CouponOut | None = None
    customer: UserOut | None = None
    address: AddressOut | None = None
    courier: CourierOut | None = None
    address_id: UUID4 | None = None
    courier_id: UUID4 | None = None

    in_trash: bool

    model_config = ConfigDict(json_schema_extra={"example": example_order_out})


# For admin
class CreateOrderAdmin(CreateOrder):
    address_id: UUID4 | None = None
    courier_id: UUID4 | None = None
    customer_id: UUID4 | None = None

    model_config = ConfigDict(json_schema_extra={"example": {
        **example_order_in,
        'customer_id': 'valid-uuid4'
    }})


class UpdateOrderAdmin(BaseModel):
    order_items: List[ItemUpdate] = []
    shipping_charge: NonNegativeFloat = 0
    weight_charge: NonNegativeFloat = 0
    discount: NonNegativeFloat = 0
    tracking_id: str | None = None
    shipping_cost: NonNegativeFloat = 0
    cod_receivable: NonNegativeFloat = 0
    cod_received: NonNegativeFloat = 0
    cost_of_good_new: NonNegativeFloat = 0
    cost_of_good_old: NonNegativeFloat = 0
    additional_cost: NonNegativeFloat = 0
    in_trash: bool = False
    order_status: StatusIn = Field(None)
    transaction_id: UUID4 = Field(None)

    model_config = ConfigDict(
        json_schema_extra={"example": example_order_update_admin})


class OrderOutAdmin(OrderOut):
    shipping_cost: NonNegativeFloat
    cod_receivable: NonNegativeFloat
    cod_received: NonNegativeFloat
    cost_of_good_new: NonNegativeFloat
    cost_of_good_old: NonNegativeFloat
    additional_cost: NonNegativeFloat
    gross_profit: FiniteFloat

    model_config = ConfigDict(
        json_schema_extra={"example": example_order_out_admin})
