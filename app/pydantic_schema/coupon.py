from pydantic import ConfigDict, Field, UUID4, field_validator, FutureDatetime, ValidationInfo
from datetime import datetime, timedelta

from app.pydantic_schema.mixins import IdTimestampMixin
from app.pydantic_schema.base import BaseModel
from app.pydantic_schema.common import BookOut, AuthorOut, PublisherOut, CategoryOut, TagOut, UserOut

from app.constant.discount_type import DiscountType
from app.constant.condition import Condition

example_coupon_base = {
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
}

example_coupon_in = {
    **example_coupon_base,
    'include_books': ['example-uuid'],
    'include_authors': ['example-uuid'],
    'include_categories': ['example-uuid'],
    'include_publishers': ['example-uuid'],
    'include_tags': ['example-uuid'],

    'exclude_books': ['example-uuid'],
    'exclude_authors': ['example-uuid'],
    'exclude_categories': ['example-uuid'],
    'exclude_publishers': ['example-uuid'],
    'exclude_tags': ['example-uuid'],

    'allowed_users': ['example-uuid'],
}

example_coupon_out = {
    **IdTimestampMixin._example,
    **example_coupon_in,
    'include_books': [BookOut._example],
    'include_authors': [AuthorOut._example],
    'include_categories': [CategoryOut._example],
    'include_publishers': [PublisherOut._example],
    'include_tags': [TagOut._example],

    'exclude_books': [BookOut._example],
    'exclude_authors': [AuthorOut._example],
    'exclude_categories': [CategoryOut._example],
    'exclude_publishers': [PublisherOut._example],
    'exclude_tags': [TagOut._example],

    'allowed_users': [UserOut._example],
}

example_coupon_out_admin = {
    **example_coupon_out,
    'use_count': 0,
    'discount_given_old': 0,
    'discount_given_new': 0,
}


class CouponBase(BaseModel):
    code: str = Field(min_length=3, max_length=20)
    short_description: str | None = Field(None, max_length=100)
    expiry_date: FutureDatetime | None = None

    discount_type: DiscountType
    discount_old: float
    discount_new: float
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

    @field_validator('discount_old', 'discount_new')
    @classmethod
    def validate_percentage_discount(cls, v: float, info: ValidationInfo):
        if info.data['discount_type'] == DiscountType.percentage:
            if not 0 <= v <= 100:
                raise ValueError(
                    'Discount must be between 0 and 100 for percent type.')
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

    model_config = ConfigDict(json_schema_extra={"example": example_coupon_in})


class UpdateCoupon(CreateCoupon):
    code: str = Field(None, min_length=3, max_length=20)
    discount_type: DiscountType = Field(None)
    discount_old: float = 0
    discount_new: float = 0

class CouponOut(CreateCoupon, IdTimestampMixin):
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
                                                 example_coupon_out})


class CouponOutAdmin(CouponOut):
    use_count: int
    discount_given_old: float
    discount_given_new: float

    model_config = ConfigDict(json_schema_extra={
                              "example": example_coupon_out_admin})


class CouponOutBulk(CouponBase, IdTimestampMixin):
    pass

class CouponOutAdminBulk(CouponBase, IdTimestampMixin):
    use_count: int
    discount_given_old: float
    discount_given_new: float

