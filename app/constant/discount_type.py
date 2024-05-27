from enum import Enum

class DiscountType(str, Enum):
    fixed_amount = 'fixed-amount'
    percentage = 'percentage'
    