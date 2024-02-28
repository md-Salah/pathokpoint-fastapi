from pydantic import BaseModel, ConfigDict

from app.pydantic_schema.mixins import TimestampMixin, timestamp_mixin_example

example_category = {
        'name': 'Fiction',
        'slug': 'fiction',
        
        'description': None,
        'image': 'https://example.com/fiction-logo.jpg',
        'banner': 'https://example.com/fiction-banner.jpg',
        'tags': [],
        
        'is_islamic': False,
        'is_english_featured': False,
        'is_bangla_featured': False,
        'is_job_featured': False,
        'is_comics': False,
    }

class CategoryBase(BaseModel):
    name: str
    slug: str
    
    description: str | None = None
    image: str | None = None
    banner: str | None = None
    tags: list[str] = []
    
    is_islamic: bool = False
    is_english_featured: bool = False
    is_bangla_featured: bool = False
    is_job_featured: bool = False
    is_comics: bool = False

    model_config = ConfigDict(json_schema_extra={"example": example_category})
    
class CreateCategory(CategoryBase):
    pass
    
class UpdateCategory(CategoryBase):
    name: str | None = None
    slug: str | None = None
    
class CategoryOut(CategoryBase, TimestampMixin):
    model_config = ConfigDict(json_schema_extra={"example": 
        example_category | timestamp_mixin_example})
    
    
    
    
    