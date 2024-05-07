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
    'image_id': 'valid-uuid4',
    'banner_id': 'valid-uuid4'
}

example_author_out = {
    **example_author_in,
    **IdTimestampMixin._example,
    'image': ImageOut._example,
    'banner': ImageOut._example,
    'followers_count': 100
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
    image_id: UUID4 | None = None
    banner_id: UUID4 | None = None

    model_config = ConfigDict(json_schema_extra={"example": example_author_in})


class UpdateAuthor(NameSlugMixinOptional, CreateAuthor):
    pass


class AuthorOut(CreateAuthor, IdTimestampMixin):
    image: ImageOut | None
    banner: ImageOut | None
    followers_count: NonNegativeInt = 0

    model_config = ConfigDict(json_schema_extra={"example":
                                                 example_author_out})
