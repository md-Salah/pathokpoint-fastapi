from pydantic import ConfigDict, Field
from datetime import datetime
from uuid import UUID
from app.pydantic_schema.base import BaseModel
from typing import ClassVar

name_regex = r'^[^\n\t_]+$'
slug_regex = r'^[a-z0-9]+(?:-[a-z0-9]+)*$'

class IdTimestampMixin(BaseModel):
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
    _example: ClassVar = {
        "id": "5b36385d-27bf-47dd-9126-df04bccfc773",
        "created_at": "2024-02-27T18:05:58.659365Z",
        "updated_at": "2024-02-27T18:05:58.659365Z"
    }

class NameSlugMixin(BaseModel):
    name: str = Field(..., min_length=3, max_length=100, pattern=name_regex)
    slug: str = Field(..., min_length=3, max_length=100, pattern=slug_regex)
    
class NameSlugMixinOptional(BaseModel):
    name: str | None = Field(None, min_length=3, max_length=100, pattern=name_regex)
    slug: str | None = Field(None, min_length=3, max_length=100, pattern=slug_regex)
    
class IdNameSlugMixin(NameSlugMixin):
    id: UUID
