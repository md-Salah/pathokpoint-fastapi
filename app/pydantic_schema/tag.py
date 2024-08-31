from pydantic import ConfigDict

from app.pydantic_schema.mixins import NameSlugMixin, NameSlugMixinOptional, IdTimestampMixin

example_tag = {
    'name': 'indian bangla books',
    'slug': 'indian-bangla-books',
    'private': True,
    'is_in_menu': True,
    'is_in_hero': True
}

example_tag_in = {
    **example_tag,
}

example_tag_out = {
    **IdTimestampMixin._example,
    **example_tag,
}


class TagBase(NameSlugMixin):
    private: bool = False
    is_in_menu: bool = False
    is_in_hero: bool = False


class CreateTag(TagBase):
    model_config = ConfigDict(json_schema_extra={"example": example_tag})


class UpdateTag(NameSlugMixinOptional, CreateTag):
    pass


class TagOut(TagBase, IdTimestampMixin):
    model_config = ConfigDict(json_schema_extra={"example":
                                                 example_tag})
