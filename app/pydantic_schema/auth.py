from pydantic import EmailStr, SecretStr, ConfigDict

from app.pydantic_schema.base import BaseModel
from app.pydantic_schema.user import UserOut

class VerifyOTP(BaseModel):
    email: EmailStr
    otp: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    
    model_config = ConfigDict(
        json_schema_extra={"example": {
            'access_token': 'example-access-token',
            'token_type': 'Bearer'
            }}) 
    
class ResetPassword(BaseModel):
    email: EmailStr
    
class SetNewPassword(BaseModel):
    email: EmailStr
    otp: str 
    new_password: SecretStr 
    
class UserOutWithToken(BaseModel):
    user: UserOut
    token: TokenResponse
