from pydantic import ConfigDict, NonNegativeInt, UUID4, Field

from app.pydantic_schema.mixins import NameSlugMixin, NameSlugMixinOptional, IdTimestampMixin
from app.pydantic_schema.common import ImageOut

from app.constant import Country

example_publisher = {
    'name': 'Rupa Publications',
    'slug': 'rupa-publications',
    'description': 'The House of Bestsellers',
    'is_islamic': False,
    'is_english': True,
    'is_popular': True,
    'is_big_sale': False,
    'country': Country.US,
    'book_published': 200,
}

example_publisher_in = {
    **example_publisher,
    'image': '5b36385d-27bf-47dd-9126-df04bccfc773',
    'banner': '5b36385d-27bf-47dd-9126-df04bccfc773',
}

example_publisher_out = {
    **IdTimestampMixin._example,
    **example_publisher,
    'image': ImageOut._example,
    'banner': ImageOut._example,
}


class PublisherBase(NameSlugMixin):
    description: str | None = Field(None, max_length=500)
    is_islamic: bool = False
    is_english: bool = False
    is_popular: bool = False
    is_big_sale: bool = False

    country: Country | None = None
    book_published: NonNegativeInt | None = None


class CreatePublisher(PublisherBase):
    image: UUID4 | None = None
    banner: UUID4 | None = None

    model_config = ConfigDict(
        json_schema_extra={"example": example_publisher_in})


class UpdatePublisher(NameSlugMixinOptional, CreatePublisher):
    pass


class PublisherOut(PublisherBase, IdTimestampMixin):
    image: ImageOut | None = None
    banner: ImageOut | None = None

    model_config = ConfigDict(json_schema_extra={"example":
                                                 example_publisher_out})
