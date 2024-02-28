from pydantic import BaseModel, ConfigDict
from datetime import datetime
from uuid import UUID

class TimestampMixin(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    created_at: datetime
    updated_at: datetime
    
timestamp_mixin_example = {
    "id": "5b36385d-27bf-47dd-9126-df04bccfc773",
    "created_at": "2024-02-27T18:05:58.659365Z",
    "updated_at": "2024-02-27T18:05:58.659365Z"
}