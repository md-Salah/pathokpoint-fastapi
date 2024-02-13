from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

class CreateOrder(BaseModel):
    books: List[int]
    shipping_method: int
    coupon_code: Optional[str] = None
    transaction_ids: List[str] = []
    status: Optional[str] = 'order placed'
    
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
    