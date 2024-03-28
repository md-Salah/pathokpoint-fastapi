from pydantic import ConfigDict, Field, AnyUrl

from app.pydantic_schema.mixins import IdTimestampMixin
from app.pydantic_schema.base import BaseModel

example_image = {
    'name': 'cover photo',
    'alt': 'cover photo',
}
example_image_out = {
    **example_image,
    **IdTimestampMixin._example,
    'src' : 'https://example.com/image.jpg',
}

class ImageBase(BaseModel):
    name: str = Field(min_length=3, max_length=100)
    alt: str = Field(max_length=100)


class ImageOut(ImageBase, IdTimestampMixin):
    src: AnyUrl
    model_config = ConfigDict(json_schema_extra={"example": example_image_out}) # type: ignore

