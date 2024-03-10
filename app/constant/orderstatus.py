from enum import Enum


class Status(Enum):
    # initial status
    pending_payment = 'pending payment'
    order_confirmed = 'order confirmed'

    processing = 'processing'
    pending_customer_confirmation = 'pending customer confirmation'
    customer_confirmed = 'customer confirmed'
    packaging_completed = 'packaging completed'
    on_delivery = 'on delivery'
    delivered = 'delivered'
    cancelled = 'cancelled'

    # Additional status
    returned = 'returned'
    on_hold = 'on hold'
    trash = 'trash'
