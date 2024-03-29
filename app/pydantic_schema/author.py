from pydantic import ConfigDict, NonNegativeInt, Field, UUID4, PastDate

from app.pydantic_schema.mixins import NameSlugMixin, NameSlugMixinOptional, IdTimestampMixin
from app.pydantic_schema.common import ImageOut
from app.constant import Country

example_author = {
        'name': 'হুমায়ূন আহমেদ',
        'slug': 'humayun-ahmed',
        'description': 'বাংলাদেশের প্রখ্যাত লেখক',
        'birth_date': '1948-11-13',
        'death_date': '2012-07-19',
        'book_published': 200,
        'city': 'dhaka',
        'country': Country.BD,
        'is_popular': True
    }

example_author_in = {
    **example_author,
    'image': '9ebd0730-5535-4485-8a8d-a2d6e1c217c4',
    'banner': '2380aebb-a968-4f8a-8bcc-5002d315fcc9'
}

example_author_out = {
    **example_author,
    **IdTimestampMixin._example,
    'image': ImageOut._example,
    'banner': ImageOut._example,
}

class AuthorBase(NameSlugMixin):
    description: str | None = Field(None, max_length=500)
    birth_date: PastDate | None = None
    death_date: PastDate | None = None
    book_published: NonNegativeInt | None = 0
    city: str | None = None
    country: Country | None = None
    is_popular: bool = False

class CreateAuthor(AuthorBase):
    image: UUID4 | None = None
    banner: UUID4 | None = None
    
    model_config = ConfigDict(json_schema_extra={"example": example_author_in})
    
class UpdateAuthor(NameSlugMixinOptional, CreateAuthor):
    pass
    
class AuthorOut(AuthorBase, IdTimestampMixin):
    image: ImageOut | None
    banner: ImageOut | None
    
    model_config = ConfigDict(json_schema_extra={"example": 
        example_author_out})
    
    
    
    
    