from pydantic import ConfigDict, UUID4

from app.pydantic_schema.mixins import NameSlugMixin, NameSlugMixinOptional, IdTimestampMixin
from app.pydantic_schema.common import CategoryOut as ParentChildCategory, ImageOut

from typing import List

example_category = {
    'name': 'Fiction',
    'slug': 'fiction',

    'description': 'This is a fiction category',
    'is_islamic': False,
    'is_english_featured': False,
    'is_bangla_featured': False,
    'is_job_featured': False,
    'is_comics': False,
    'is_popular': False,
    'is_big_sale': False,
}

example_category_in = {
    **example_category,
    'image_id': 'valid-uuid4',
    'banner_id': 'valid-uuid4',
    'parent': ['valid-uuid4'],
}

example_category_out = {
    **example_category_in,
    **IdTimestampMixin._example,
    'image': ImageOut._example,
    'banner': ImageOut._example,
    'parent': ParentChildCategory._example,
    'children': ParentChildCategory._example,
}


class CategoryBase(NameSlugMixin):
    description: str | None = None
    is_islamic: bool = False
    is_english_featured: bool = False
    is_bangla_featured: bool = False
    is_job_featured: bool = False
    is_comics: bool = False
    is_popular: bool = False
    is_big_sale: bool = False


class CreateCategory(CategoryBase):
    parent: List[UUID4] = []
    image_id: UUID4 | None = None
    banner_id: UUID4 | None = None

    model_config = ConfigDict(
        json_schema_extra={"example": example_category_in})


class UpdateCategory(NameSlugMixinOptional, CreateCategory):
    pass

class CategoryOut(CreateCategory, IdTimestampMixin):
    image: ImageOut | None = None
    banner: ImageOut | None = None
    parent: list[ParentChildCategory] | None = None
    # children: list[ParentChildCategory] | None = None

    model_config = ConfigDict(json_schema_extra={"example":
                                                 example_category_out})

