from fastapi import Query
from pydantic import Field
from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import field_validator

from app.models.coupon import Coupon


class CouponFilter(Filter):
    q: str | None = Field(Query(None, description='Search by coupon code or description'))
    is_active: bool | None = None
    order_by: list[str] | None = Field(Query(None, description='Sort by fields created_at, expiry_date, discount_old, discount_new. Add "-" for descending order'))
    
    @field_validator('order_by')
    def restrict_sortable_fields(cls, value):
        if value is None:
            return None
        
        allowed_fields = ['created_at', 'expiry_date', 'discount_old', 'discount_new']
        
        for field_name in value:
            field_name = field_name.replace('-', '').replace('+', '')
            if field_name not in allowed_fields:
                raise ValueError('You may only sort by {}'.format(', '.join(allowed_fields)))
        return value

    class Constants(Filter.Constants):
        model = Coupon
        search_field_name = 'q'
        search_model_fields = ['code', 'short_description']
        
        