from pydantic import ConfigDict, Field

from app.pydantic_schema.mixins import TimestampMixin, timestamp_mixin_example
from app.pydantic_schema.base import BaseModel

example_tag = {
    'name': 'indian bangla books',
    'slug': 'indian-bangla-books',
    'private': True,
}

class TagBase(BaseModel):
    name: str = Field(min_length=3, max_length=100)
    slug: str = Field(min_length=3, max_length=100)
    private: bool = False

    model_config = ConfigDict(json_schema_extra={"example": example_tag})


class CreateTag(TagBase):
    pass


class UpdateTag(TagBase):
    name: str | None = Field(min_length=3, max_length=100, default=None)
    slug: str | None = Field(min_length=3, max_length=100, default=None)
    private: bool | None = None


class TagOut(TagBase, TimestampMixin):
    model_config = ConfigDict(json_schema_extra={"example":
                                                 example_tag | timestamp_mixin_example})
