import pydantic
from pydantic import ConfigDict


class BaseModel(pydantic.BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, 
                              str_to_lower=False,
                              use_enum_values=False, 
                              arbitrary_types_allowed=True,
                              )
    



