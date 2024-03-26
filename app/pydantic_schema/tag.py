from pydantic import ConfigDict

from app.pydantic_schema.mixins import NameSlugMixin, NameSlugMixinOptional, TimestampMixin, timestamp_mixin_example

example_tag = {
    'name': 'indian bangla books',
    'slug': 'indian-bangla-books',
    'private': True,
}

class TagBase(NameSlugMixin):
    private: bool = False

    model_config = ConfigDict(json_schema_extra={"example": example_tag})


class CreateTag(TagBase):
    pass


class UpdateTag(NameSlugMixinOptional, CreateTag):
    pass


class TagOut(TagBase, TimestampMixin):
    model_config = ConfigDict(json_schema_extra={"example":
                                                 example_tag | timestamp_mixin_example})
