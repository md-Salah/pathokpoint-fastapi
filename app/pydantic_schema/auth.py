from app.pydantic_schema.base import BaseModel

class TokenResponse(BaseModel):
    access_token: str
    token_type: str