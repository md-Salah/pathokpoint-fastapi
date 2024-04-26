from pydantic import UUID4, ConfigDict
from typing import List

from app.pydantic_schema.base import BaseModel
from app.pydantic_schema.mixins import IdTimestampMixin
from app.pydantic_schema.common import UserOut, CouponOut, CourierOut
from app.pydantic_schema.transaction import TransactionOut
from app.pydantic_schema.address import AddressOut
from app.pydantic_schema.order_item import ItemIn, ItemOut, ItemUpdate
from app.pydantic_schema.order_status import StatusIn, StatusOut

example_order_in = {
    'order_items': [ItemIn._example],
    'coupon_id': 'valid-uuid4',
    'customer_id': 'valid-uuid4',
    'address_id': 'valid-uuid4',
    'courier_id': 'valid-uuid4',
}
example_order_update = {
    **example_order_in,
    'order_items': [ItemUpdate._example],
    'order_status': [StatusIn._example],
    'transactions': ['valid-uuid4'],
    'in_trash': False,
}

example_order_out = {
    **IdTimestampMixin._example,
    'invoice': 1,
    'order_items': [ItemOut._example],
    'new_book_total': 400,
    'old_book_total': 100,
    'shipping_charge': 100,
    'weight_charge': 0,
    'total': 600,
    'discount': 100,
    'payable': 500,
    'paid': 500,
    'payment_back': 0,
    'cash_on_delivery': 0,
    'refunded': 0,
    'customer_note': 'Valo boi diben',
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
    '_shipping_cost': 0,
    '_cod_receivable': 0,
    '_cod_received': 0,
    '_new_cost': 0,
    '_old_cost': 0,
    '_additional_cost': 0,
    '_outcome': 0,
}

class OrderBase(BaseModel):
    pass
    
class CreateOrder(OrderBase):
    order_items: List[ItemIn]
    coupon_id: UUID4 | None = None
    address_id: UUID4 | None = None
    courier_id: UUID4 | None = None
    
    model_config = ConfigDict(json_schema_extra={"example": example_order_in})

class CreateOrderAdmin(CreateOrder):
    customer_id: UUID4 | None = None
    
class UpdateOrder(CreateOrder):
    order_items: List[ItemUpdate] = []
    order_status: StatusIn | None = None
    transactions: List[UUID4] = []
    in_trash: bool = False
    
    model_config = ConfigDict(json_schema_extra={"example": example_order_update})

class OrderOut(OrderBase, IdTimestampMixin):
    invoice: int
    order_items: List[ItemOut]
    new_book_total: float
    old_book_total: float
    shipping_charge: float
    weight_charge: float = 0
    total: float
    discount: float = 0
    payable: float
    paid: float
    payment_back: float = 0
    cash_on_delivery: float
    refunded: float = 0
    
    customer_note: str | None = None
    
    order_status: List[StatusOut]
    transactions: List[TransactionOut] = []
    coupon: CouponOut | None = None
    customer: UserOut | None = None
    address: AddressOut | None = None
    courier: CourierOut | None = None
    
    in_trash: bool
    
    model_config = ConfigDict(json_schema_extra={"example": example_order_out})

class OrderOutAdmin(OrderOut):
    _shipping_cost: float = 0
    _cod_receivable: float = 0
    _cod_received: float = 0
    _new_cost: float = 0
    _old_cost: float = 0
    _additional_cost: float = 0
    _outcome: float = 0
    
    model_config = ConfigDict(json_schema_extra={"example": example_order_out_admin})

    