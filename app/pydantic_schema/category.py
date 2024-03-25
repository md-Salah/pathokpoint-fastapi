from pydantic import ConfigDict, UUID4, Field

from app.pydantic_schema.mixins import IdTimestampMixin, id_timestamp_mixin_example
from app.pydantic_schema.base import BaseModel
from app.pydantic_schema.image import ImageOut, example_image_out

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
    'image': '5b36385d-27bf-47dd-9126-df04bccfc773',
    'banner': '5b36385d-27bf-47dd-9126-df04bccfc773',
    'parent': ['5b36385d-27bf-47dd-9126-df04bccfc773'],
}

example_category_out = {
    **example_category,
    'image': example_image_out,
    'banner': example_image_out,
    'parent': [{'id': '5b36385d-27bf-47dd-9126-df04bccfc773', 'name': 'Fiction', 'slug': 'fiction'}],
    'children': [{'id': '5b36385d-27bf-47dd-9126-df04bccfc773', 'name': 'Fiction', 'slug': 'fiction'}],
}


class CategoryBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    slug: str = Field(..., min_length=3, max_length=100,
                      pattern=r'^[a-z0-9]+(?:-[a-z0-9]+)*$')

    description: str | None = None
    is_islamic: bool = False
    is_english_featured: bool = False
    is_bangla_featured: bool = False
    is_job_featured: bool = False
    is_comics: bool = False
    is_popular: bool = False
    is_big_sale: bool = False


class CreateCategory(CategoryBase):
    image: UUID4 | None = None
    banner: UUID4 | None = None

    model_config = ConfigDict(
        json_schema_extra={"example": example_category_in})


class UpdateCategory(CategoryBase):
    name: str | None = Field(None, min_length=3, max_length=100)
    slug: str | None = Field(
        None, min_length=3, max_length=100, pattern=r'^[a-z0-9]+(?:-[a-z0-9]+)*$')

class CategoryOut(CategoryBase, IdTimestampMixin):
    class CategoryRelationship(BaseModel):
        id: UUID4
        name: str
        slug: str
    
    image: ImageOut | None = None
    banner: ImageOut | None = None
    # parent: list[CategoryRelationship] | None = None
    # children: list[CategoryRelationship] | None = None

    model_config = ConfigDict(json_schema_extra={"example":
                                                 example_category_out | id_timestamp_mixin_example})
