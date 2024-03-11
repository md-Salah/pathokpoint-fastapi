from pydantic import ConfigDict, Field, AnyUrl

from app.pydantic_schema.mixins import TimestampMixin, timestamp_mixin_example
from app.pydantic_schema.base import BaseModel

example_image = {
    'name': 'The God of Small Things',
    'alt': 'The God of Small Things book cover image',
}
example_image_out = {
    **example_image,
    'src' : 'https://example.com/image.jpg',
}

class ImageBase(BaseModel):
    name: str = Field(min_length=3, max_length=100)
    alt: str = Field(max_length=100)

    model_config = ConfigDict(json_schema_extra={"example": example_image}) # type: ignore



class ImageOut(ImageBase, TimestampMixin):
    src: AnyUrl
    model_config = ConfigDict(json_schema_extra={"example":
                                                 example_image_out | timestamp_mixin_example}) # type: ignore

