import pydantic
from pydantic import ConfigDict


class BaseModel(pydantic.BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, 
                              use_enum_values=False, 
                              arbitrary_types_allowed=True,
                              )
    
    pass
