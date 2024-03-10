from pydantic import ConfigDict, Field

from app.pydantic_schema.mixins import TimestampMixin, timestamp_mixin_example
from app.pydantic_schema.base import BaseModel

example_image = {
    'name': 'The God of Small Things',
    'src' : 'https://example.com/image.jpg',
    'alt': 'The God of Small Things book cover image',
    'dummy': False
}

class ImageBase(BaseModel):
    name: str = Field(min_length=3, max_length=100)
    src: str = Field(min_length=3, max_length=1000)
    alt: str = Field(min_length=3, max_length=100)

    model_config = ConfigDict(json_schema_extra={"example": example_image})


class CreateImage(ImageBase):
    pass


class UpdateImage(ImageBase):
    name: str | None = Field(min_length=3, max_length=100, default=None)
    slug: str | None = Field(min_length=3, max_length=100, default=None)
    private: bool | None = None


class ImageOut(ImageBase, TimestampMixin):
    model_config = ConfigDict(json_schema_extra={"example":
                                                 example_image | timestamp_mixin_example})

