import enum


class DiscountType(enum.Enum):
    fixed_amount = 'fixed_amount'
    percentage = 'percentage'
    flat_rate = 'flat_rate'