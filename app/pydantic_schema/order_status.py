from pydantic import UUID4
from typing import ClassVar

from app.pydantic_schema.base import BaseModel
from app.pydantic_schema.mixins import IdTimestampMixin
from app.pydantic_schema.common import UserOut
from app.constant.orderstatus import Status

class StatusBase(BaseModel):
    status: Status
    note: str | None = None
    _admin_note: str | None = None
    
    _example: ClassVar = {
        'status': Status.order_confirmed,
        'note': 'This is a note',
        '_admin_note': 'This is an admin note',
    }

class StatusIn(StatusBase):
    admin_id: UUID4 | None = None
    _example: ClassVar = {
        'admin_id': 'valid-uuid4',
        **StatusBase._example
    }
    
class StatusOut(StatusBase, IdTimestampMixin):
    updated_by: UserOut | None
    
    _example: ClassVar = {
        **StatusBase._example,
        'updated_by': UserOut._example
    }
    