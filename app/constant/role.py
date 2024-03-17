import enum

class Role(enum.Enum):
    customer = 'customer'
    staff = 'staff'
    admin = 'admin'
    super_admin = 'super_admin'