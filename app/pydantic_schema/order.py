from typing import List, Optional
from datetime import datetime
from pydantic import UUID4

from app.pydantic_schema.base import BaseModel

class OrderItem(BaseModel):
    book_id: UUID4
    quantity: int

class CreateOrder(BaseModel):
    user_id: UUID4
    items: List[OrderItem]
    shipping_method_id: UUID4
    coupon_ids: List[UUID4] = []
    transaction_ids: List[UUID4] = []
    address_id: UUID4
    
class UpdateOrder(CreateOrder):
    pass

class OrderBase(CreateOrder):
    id: int
    new_book_total: float
    old_book_total: float
    shipping_charge: float
    weight_charge: Optional[float] = 0
    total: float
    discount: Optional[float] = 0
    payable: float
    paid: float
    refunded: Optional[float] = 0
    due: float
    
    date_created: datetime
    date_updated: datetime
    
class ReadOrder(OrderBase):
    pass

    
class DeleteOrder(BaseModel):
    msg: str
    
    
class FilterOrder(BaseModel):
    id: Optional[int]
    phone_number: Optional[str]
    email: Optional[str]
    status: Optional[str]
    transaction_id: Optional[str]
    