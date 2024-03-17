from pydantic import EmailStr, SecretStr, ConfigDict

from app.pydantic_schema.base import BaseModel
from app.pydantic_schema.user import UserOut

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    
    model_config = ConfigDict(
        json_schema_extra={"example": {
            'access_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6ImUwNzBmODYyLTYzMjQtNDMzMS1iZGJjLWJmOTZjOWJhNWI0ZSIsInJvbGUiOiJSb2xlLmFkbWluIiwiZXhwaXJlcyI6MTcxMDcwMDE3MC45NDUzNDMsInR5cGUiOiJ2ZXJpZmljYXRpb24ifQ.LoVxelAnd4JG1aj5UhNtiEjUsLhUEoeNdXZmr3tj1Vc',
            'token_type': 'Bearer'
            }}) 
    
class ResetPassword(BaseModel):
    email: EmailStr
    
class SetNewPassword(BaseModel):
    token: str 
    new_password: SecretStr 
    
class UserOutWithToken(BaseModel):
    user: UserOut
    token: TokenResponse
