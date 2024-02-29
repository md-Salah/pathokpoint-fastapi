from pydantic import ConfigDict
from datetime import date

from app.pydantic_schema.mixins import TimestampMixin, timestamp_mixin_example
from app.pydantic_schema.base import BaseModel

example_author = {
        'name': 'হুমায়ূন আহমেদ',
        'slug': 'humayun-ahmed',
        'description': 'বাংলাদেশের প্রখ্যাত লেখক',
        'image': 'https://example.com/humayun-ahmed.jpg',
        'banner': 'https://example.com/humayun-ahmed-banner.jpg',
        'birth_date': '1948-11-13',
        'death_date': '2012-07-19',
        'book_published': 200,
        'tags': ['বাংলা', 'উপন্যাস', 'গল্প'],
        'city': 'dhaka',
        'country': 'bangladesh',
        'is_popular': True
    }

class AuthorBase(BaseModel):
    name: str
    slug: str
    
    description: str | None = None
    image: str | None = None
    banner: str | None = None
    
    birth_date: date | None = None
    death_date: date | None = None
    book_published: int | None = None
    
    tags: list[str] = []

    city: str | None = None
    country: str | None = None
    is_popular: bool = False

    model_config = ConfigDict(json_schema_extra={"example": example_author})
    
class CreateAuthor(AuthorBase):
    pass
    
class UpdateAuthor(AuthorBase):
    name: str | None = None
    slug: str | None = None
    
class AuthorOut(AuthorBase, TimestampMixin):
    model_config = ConfigDict(json_schema_extra={"example": 
        example_author | timestamp_mixin_example})
    
    
    
    
    