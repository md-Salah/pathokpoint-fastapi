from pydantic import AnyUrl
from app.pydantic_schema.mixins import IdNameSlugMixin, IdTimestampMixin
from typing import ClassVar

class BookOut(IdNameSlugMixin):
    _example: ClassVar = {
        'id': "246647f1-ab80-427e-82ee-52528ea87739",
        'name': 'The Hobbit',
        'slug': 'the-hobbit',
    }


class AuthorOut(IdNameSlugMixin):
    _example: ClassVar = {
        'id': "246647f1-ab80-427e-82ee-52528ea87739",
        'name': 'হুমায়ূন আহমেদ',
        'slug': 'humayun-ahmed',
    }


class PublisherOut(IdNameSlugMixin):
    _example: ClassVar = {
        'id': "246647f1-ab80-427e-82ee-52528ea87739",
        'name': 'অনন্যা',
        'slug': 'ananya',
    }


class CategoryOut(IdNameSlugMixin):
    _example: ClassVar = {
        'id': "246647f1-ab80-427e-82ee-52528ea87739",
        'name': 'উপন্যাস',
        'slug': 'uponnas',
    }


class TagOut(IdNameSlugMixin):
    _example: ClassVar = {
        'id': "246647f1-ab80-427e-82ee-52528ea87739",
        'name': 'General Bangla',
        'slug': 'general-bangla'
    }
    
class UserOut(IdNameSlugMixin):
    _example: ClassVar = {
        'id': "246647f1-ab80-427e-82ee-52528ea87739",
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
    
