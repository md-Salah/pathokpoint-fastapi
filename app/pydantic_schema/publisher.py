from pydantic import BaseModel, ConfigDict

from app.pydantic_schema.mixins import TimestampMixin, timestamp_mixin_example

example_publisher = {
        'name': 'Rupa Publications',
        'slug': 'rupa-publications',
        
        'description': 'The House of Bestsellers',
        'image': 'https://example.com/rupa-logo.jpg',
        'banner': 'https://example.com/rupa-banner.jpg',
        'tags': [],
        
        'is_islamic': False,
        'is_english': True,
        'is_popular': True,
        
        'country': 'usa',
        'book_published': 200,
    }

class PublisherBase(BaseModel):
    name: str
    slug: str
    
    description: str | None = None
    image: str | None = None
    banner: str | None = None
    tags: list[str] = []
    
    is_islamic: bool = False
    is_english: bool = False
    is_popular: bool = False
    
    country: str | None = None
    book_published: int | None = None

    model_config = ConfigDict(json_schema_extra={"example": example_publisher})
    
class CreatePublisher(PublisherBase):
    pass
    
class UpdatePublisher(PublisherBase):
    name: str | None = None
    slug: str | None = None
    
class PublisherOut(PublisherBase, TimestampMixin):
    model_config = ConfigDict(json_schema_extra={"example": 
        example_publisher | timestamp_mixin_example})
    
    
    
    
    