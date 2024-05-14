from enum import Enum

class Role(str, Enum):
    customer = 'customer'
    admin = 'admin'
    super_admin = 'super-admin'
    staff = 'staff'