from fastapi import Query
from pydantic import Field
from fastapi_filter.contrib.sqlalchemy import Filter
from fastapi_filter import FilterDepends, with_prefix
from pydantic import field_validator, UUID4
from typing import List
from datetime import datetime

from app.models import Coupon, User, Address, Courier
from app.models.order import Order, OrderStatus
from app.constant.orderstatus import Status
from app.constant.country import Country
from app.constant.city import City

class StatusFilter(Filter):
    id: UUID4 | None = None
    status: Status | None = None
    
    class Constants(Filter.Constants):
        model = OrderStatus
        
class CouponFilter(Filter):
    id: UUID4 | None = None
    code: str | None = None
    
    class Constants(Filter.Constants):
        model = Coupon
        
class CustomerFilter(Filter):
    id: UUID4 | None = None
    username: str | None = None
    email: str | None = None
    phone_number: str | None = None
    
    class Constants(Filter.Constants):
        model = User
        
class AddressFilter(Filter):
    id: UUID4 | None = None
    phone_number: str | None = None
    thana: str | None = None
    city: City | None = None
    country: Country | None = None
    
    class Constants(Filter.Constants):
        model = Address
        
class CourierFilter(Filter):
    id__in: List[UUID4] | None = None
    method_name__in: List[str] | None = None
    company_name: str | None = None
    allow_cash_on_delivery: bool | None = None
    
    class Constants(Filter.Constants):
        model = Courier        


class OrderFilter(Filter):
    q: str | None = Field(Query(None, description='Search by id or invoice number'))
    invoice: int | None = None
    is_full_paid: bool | None = None
    shipping_charge__gte: float | None = None
    shipping_charge__lte: float | None = None
    weight_charge__gte: float | None = None
    weight_charge__lte: float | None = None
    total__gte: float | None = None
    total__lte: float | None = None
    discount__gte: float | None = None
    discount__lte: float | None = None
    net_amount__gte: float | None = None
    net_amount__lte: float | None = None
    paid__gte: float | None = None
    paid__lte: float | None = None
    due__gte: float | None = None
    due__lte: float | None = None
    refunded__gte: float | None = None
    refunded__lte: float | None = None
    tracking_id: str | None = None
    shipping_cost__gte: float | None = None
    shipping_cost__lte: float | None = None
    cod_receivable__gte: float | None = None
    cod_receivable__lte: float | None = None
    cod_received__gte: float | None = None
    cod_received__lte: float | None = None
    cost_of_good_new__gte: float | None = None
    cost_of_good_new__lte: float | None = None
    cost_of_good_old__gte: float | None = None
    cost_of_good_old__lte: float | None = None
    additional_cost__gte: float | None = None
    gross_profit__gte: float | None = None
    gross_profit__lte: float | None = None
    in_trash: bool | None = None
    created_at: datetime | None = None
    
    order_status: StatusFilter = FilterDepends(with_prefix('order_status', StatusFilter))
    coupon: CouponFilter = FilterDepends(with_prefix('coupon', CouponFilter))
    customer: CustomerFilter = FilterDepends(with_prefix('customer', CustomerFilter))
    address: AddressFilter = FilterDepends(with_prefix('address', AddressFilter))
    
    order_by: List[str] | None = Field(Query(None, description='Sort by fields invoice, total, discount, net_amount, paid, due, shipping_cost etc. Add "-" for descending order'))
    
    @field_validator('order_by')
    def restrict_sortable_fields(cls, value):
        if value is None:
            return None
        
        allowed_fields = ['invoice', 'total', 'discount', 'net_amount', 'paid', 'due', 'shipping_cost', 'cod_receivable', 'cod_received', 'gross_profit', 'created_at']
        
        for field_name in value:
            field_name = field_name.replace('-', '').replace('+', '')
            if field_name not in allowed_fields:
                raise ValueError('You may only sort by {}'.format(', '.join(allowed_fields)))
        return value

    class Constants(Filter.Constants):
        model = Order
        search_field_name = 'q'
        search_model_fields = ['id', 'invoice']
        
        