from enum import Enum


class Status(Enum):
    # initial status
    pending_payment = 'pending-payment'
    order_confirmed = 'order-confirmed'

    processing = 'processing'
    pending_condition_confirmation = 'pending-condition-confirmation' # Video has been sent to customer, waiting for confirmation
    customer_confirmed = 'customer-confirmed' # Customer has confirmed the condition
    packaging_completed = 'packaging-completed'
    on_delivery = 'on-delivery'
    delivered = 'delivered'
    cancelled = 'cancelled'

    # Additional status
    completed = 'completed' # Order has been completed, COD has been received
    returned = 'returned' 
    on_hold = 'on-hold'
    trash = 'trash'
