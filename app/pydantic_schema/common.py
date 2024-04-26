from pydantic import AnyUrl, UUID4
from typing import ClassVar

from app.pydantic_schema.mixins import IdNameSlugMixin, IdTimestampMixin
from app.pydantic_schema.base import BaseModel
from app.constant.condition import Condition

class BookOut(IdNameSlugMixin):
    condition: Condition
    _example: ClassVar = {
        'id': "valid-uuid4",
        'name': 'The Hobbit',
        'slug': 'the-hobbit',
        'condition': Condition.old_like_new
    }


class AuthorOut(IdNameSlugMixin):
    _example: ClassVar = {
        'id': "valid-uuid4",
        'name': 'হুমায়ূন আহমেদ',
        'slug': 'humayun-ahmed',
    }


class PublisherOut(IdNameSlugMixin):
    _example: ClassVar = {
        'id': "valid-uuid4",
        'name': 'অনন্যা',
        'slug': 'ananya',
    }


class CategoryOut(IdNameSlugMixin):
    _example: ClassVar = {
        'id': "valid-uuid4",
        'name': 'উপন্যাস',
        'slug': 'uponnas',
    }


class TagOut(IdNameSlugMixin):
    _example: ClassVar = {
        'id': "valid-uuid4",
        'name': 'General Bangla',
        'slug': 'general-bangla'
    }
    
class UserOut(BaseModel):
    id: UUID4
    first_name: str | None = None
    last_name: str | None = None
    username: str
    
    _example: ClassVar = {
        'id': "valid-uuid4",
        'first_name': 'John',
        'last_name': 'Doe',
        'username': 'John Doe',
    }

class ImageOut(IdTimestampMixin):
    name: str
    alt: str
    src: AnyUrl
    
    _example: ClassVar = {
        'name': 'cover photo.jpg',
        'alt': 'Cover Photo',
        'src': 'https://example.com/cover-photo.jpg',
        **IdTimestampMixin._example,
    }
    

class CouponOut(BaseModel):
    id: UUID4
    code: str
    
    _example: ClassVar = {
        'id': 'valid-uuid4',
        'code': 'NEW-USER',
    }
    
class CourierOut(BaseModel):
    id: UUID4
    method_name: str
    company_name: str
    
    _example: ClassVar = {
        'id': "valid-uuid4",
        'method_name': 'Inside dhaka home delivery',
        'company_name': 'Delivery Tiger',
    }
    
class OrderOut(BaseModel):
    id: UUID4
    invoice: int
    
    _example: ClassVar = {
        'id': "valid-uuid4",
        'invoice': 3101,
    }
    
    
class PaymentGatewayOut(BaseModel):
    id: UUID4
    name: str 
    description: str | None 
    is_enabled: bool 
    
    _example: ClassVar = {
        'id': "valid-uuid4",
        'name': 'bKash',
        'description': 'bKash Payment Gateway',
        'is_enabled': True,
    }
    