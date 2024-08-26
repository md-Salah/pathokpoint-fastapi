from typing import ClassVar

from app.pydantic_schema.base import BaseModel
from app.pydantic_schema.mixins import IdTimestampMixin
from app.pydantic_schema.common import UserOut
from app.constant.orderstatus import Status

class StatusBase(BaseModel):
    status: Status
    note: str | None = None
    
    _example: ClassVar = {
        'status': Status.order_confirmed,
        'note': 'This is a note',
    }

class StatusIn(StatusBase):
    _example: ClassVar = {
        **StatusBase._example
    }
    
class StatusOut(StatusBase, IdTimestampMixin):
    updated_by: UserOut | None
    
    _example: ClassVar = {
        **StatusBase._example,
        'updated_by': UserOut._example
    }
    