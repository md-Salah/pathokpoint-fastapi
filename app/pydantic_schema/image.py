from pydantic import ConfigDict, AnyUrl

from app.pydantic_schema.mixins import IdTimestampMixin

example_image_out = {
    **IdTimestampMixin._example,
    'name': 'image.jpg',
    'src': 'https://example.com/image.jpg',
    'public_id': 'image-public-id',
    'folder': 'book'
}


class ImageOut(IdTimestampMixin):
    name: str
    src: AnyUrl
    public_id: str
    folder: str
    model_config = ConfigDict(
        json_schema_extra={"example": example_image_out})  # type: ignore
