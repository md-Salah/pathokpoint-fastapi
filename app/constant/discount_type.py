import enum


class DiscountType(enum.Enum):
    fixed_amount = 'fixed-amount'
    percentage = 'percentage'
    flat_rate = 'flat-rate'