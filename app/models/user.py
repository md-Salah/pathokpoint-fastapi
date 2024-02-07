from enum import Enum
from typing import Optional
from sqlmodel import Field, SQLModel
from pydantic import EmailStr, validator
from fastapi import HTTPException, status

from .mixins import TimestampMixin

# Enum types
class Role(Enum):
    customer = 'customer'
    moderator = 'moderator'
    admin = 'admin'
    
# Base models
class UserBase(SQLModel):
    email : EmailStr = Field(unique=True, index=True, nullable=False)
    phone_number: Optional[str] = Field(min_length=8, max_length=15)
    first_name: Optional[str] = Field(max_length=20)
    last_name: Optional[str] = Field(max_length=20)
    
    # Relationships
    # orders = relationship('Order', back_populates='user')
    # coupons = relationship('Coupon', back_populates='user')
    # reviews = relationship('Review', back_populates='user')
    # addresses = relationship('Address', back_populates='user')
    # cards = relationship('Card', back_populates='user')
    # cart = relationship('Cart', back_populates='user')
    # wishlist = relationship('Wishlist', back_populates='user')
    # notifications = relationship('Notification', back_populates='user')
    
class UserBaseSecret(SQLModel):
    password: str = Field(nullable=False)
    
# Database table model
## table name: user
class User(UserBase, UserBaseSecret, TimestampMixin, table=True):
    id : Optional[int] = Field(primary_key=True)
    role: Role = Field(nullable=False, default=Role.customer)
    
    
# Pydantic models
## CREATE
class UserCreate(UserBase, UserBaseSecret):
    pass

class UserCreateByAdmin(UserCreate):
    role: Role = Role.customer

## READ
class UserRead(UserBase, TimestampMixin):
    id: int
    role: Role

class UserReadWithToken(UserRead):
    token: str
    
## UPDATE
class UserUpdate():
    email : Optional[EmailStr] = None
    phone_number: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class UserUpdateByAdmin(UserUpdate):
    role: Optional[Role] = None

    