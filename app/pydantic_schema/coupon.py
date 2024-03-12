from pydantic import ConfigDict, Field, UUID4, field_validator, FutureDatetime, ValidationInfo
from datetime import datetime, timedelta

from app.pydantic_schema.mixins import TimestampMixin, timestamp_mixin_example
from app.pydantic_schema.base import BaseModel
from app.pydantic_schema.author import AuthorOut
from app.pydantic_schema.category import CategoryOut
from app.pydantic_schema.publisher import PublisherOut
from app.pydantic_schema.tag import TagOut
from app.pydantic_schema.book import BookOut
from app.pydantic_schema.user import UserOut

from app.constant.discount_type import DiscountType
from app.constant.condition import Condition

example_coupon = {
    'code': 'new-user',
    'short_description': 'New User Discount',
    'expiry_date': datetime.now() + timedelta(days=30),
    'discount_type': DiscountType.percentage,
    'discount_old': 10,
    'discount_new': 25,
    'max_discount_old': -1,
    'max_discount_new': 200,
    'min_spend_old': 499,
    'min_spend_new': 1499,
    
    'use_limit': 100,
    'use_limit_per_user': 1,
    'individual_use': True,
    'is_active': True,
    'free_shipping': False,
    'include_conditions': [Condition.old_like_new],
    
    'include_books': [],
    'include_authors': [],
    'include_categories': [],
    'include_publishers': [],
    'include_tags': [],
    
    'exclude_books': [],
    'exclude_authors': [],
    'exclude_categories': [],
    'exclude_publishers': [],
    'exclude_tags': [],
    
    'allowed_users': [],
    
}

example_coupon_admin = {
    **example_coupon,
    'use_count': 0,
    'discount_given_old': 0,
    'discount_given_new': 0,
}

class CouponBase(BaseModel):
    code: str = Field(min_length=3, max_length=20)
    short_description: str | None = Field(None, max_length=100)
    expiry_date: FutureDatetime | None = None
    
    discount_type: DiscountType
    discount_old: float = 0
    discount_new: float = 0
    max_discount_old: float = -1
    max_discount_new: float = -1
    min_spend_old: float = 0
    min_spend_new: float = 0
    
    use_limit: int = -1
    use_limit_per_user: int = -1
    individual_use: bool = False
    is_active: bool = True
    free_shipping: bool = False
    include_conditions: list[Condition] = []

    model_config = ConfigDict(json_schema_extra={"example": example_coupon})
    
    @field_validator('discount_old', 'discount_new')
    @classmethod
    def validate_percentage_discount(cls, v: float, info: ValidationInfo):
        if info.data['discount_type'] == DiscountType.percentage:
            if not 0 <= v <= 100:
                raise ValueError('Discount must be between 0 and 100 for percent type.')
        return v

class CreateCoupon(CouponBase):
    include_books: list[UUID4] = []
    include_authors: list[UUID4] = []
    include_categories: list[UUID4] = []
    include_publishers: list[UUID4] = []
    include_tags: list[UUID4] = []
    
    exclude_books: list[UUID4] = []
    exclude_authors: list[UUID4] = []
    exclude_categories: list[UUID4] = []
    exclude_publishers: list[UUID4] = []
    exclude_tags: list[UUID4] = []
    
    allowed_users: list[UUID4] = []


class UpdateCoupon(CreateCoupon):
    code: str | None = Field(None, min_length=3, max_length=20)
    discount_type: DiscountType | None = None


class CouponOut(CouponBase, TimestampMixin):
    include_books: list[BookOut] = []
    include_authors: list[AuthorOut] = []
    include_categories: list[CategoryOut] = []
    include_publishers: list[PublisherOut] = []
    include_tags: list[TagOut] = []
    
    exclude_books: list[BookOut] = []
    exclude_authors: list[AuthorOut] = []
    exclude_categories: list[CategoryOut] = []
    exclude_publishers: list[PublisherOut] = []
    exclude_tags: list[TagOut] = []
    
    allowed_users: list[UserOut] = []
    
    model_config = ConfigDict(json_schema_extra={"example":
                                                 example_coupon | timestamp_mixin_example})

class CouponOutAdmin(CouponOut):
    use_count: int
    discount_given_old: float
    discount_given_new: float
    
    model_config = ConfigDict(json_schema_extra={"example": example_coupon_admin | timestamp_mixin_example})
    