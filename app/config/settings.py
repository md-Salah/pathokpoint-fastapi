from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import ValidationError, EmailStr
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = 'PATHOK POINT'
    PROJECT_DESCRIPTION: str = 'Ecommerce backend for the bookshop PATHOK POINT'
    PROJECT_VERSION: str = '1.0.0'

    PRODUCTION: bool = False
    BASE_URL: str = "http://localhost:8000"
    FRONTEND_URL: str = "http://localhost:3000"
    LOGO_URL: str
    ADMIN_EMAILS: List[EmailStr] = []

    DATABASE_URL: str
    TEST_DATABASE_URL: str

    REDIS_URL: str

    JWT_SECRET: str
    JWT_REFRESH_SECRET_KEY: str
    JWT_ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # in mins

    SMTP_SERVER: str
    SMTP_PORT: int
    SMTP_USERNAME: str
    SMTP_PASSWORD: str

    BKASH_URL: str
    BKASH_USERNAME: str
    BKASH_PASSWORD: str
    BKASH_APP_KEY: str
    BKASH_APP_SECRET: str
    
    FASTAPI_ANALYTICS_API_KEY: str
    
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION: str
    BUCKET_NAME: str

    model_config = SettingsConfigDict(env_file='.env', extra='allow')


try:
    settings = Settings()  # type: ignore
except ValidationError as err:
    print(err)
    exit(1)
