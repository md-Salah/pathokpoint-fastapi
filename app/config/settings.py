from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import ValidationError

class Settings(BaseSettings):
    PROJECT_NAME: str = 'PATHOK POINT'
    PROJECT_DESCRIPTION: str = 'Ecommerce backend for the bookshop PATHOK POINT'
    PROJECT_VERSION: str = '1.0.0'
    
    DATABASE_URL: str
    TEST_DATABASE_URL: str
    
    JWT_SECRET: str
    JWT_REFRESH_SECRET_KEY: str
    
    JWT_ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # in mins
    
    CLOUDINARY_CLOUD_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str

    PRODUCTION: bool

    model_config = SettingsConfigDict(env_file='.env', extra='allow')
    
try:
    settings = Settings() # type: ignore
except ValidationError as err:
    print(err)
    exit(1)
    
    