from enum import Enum


class Status(str, Enum):
    # status
    pending = 'pending'
    processing = 'processing'
    on_delivery = 'on-delivery'
    delivered = 'delivered'

    # Additional status
    cancelled = 'cancelled'
