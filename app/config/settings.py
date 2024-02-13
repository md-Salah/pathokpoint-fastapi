import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    def __init__(self):
        self.POSTGRES_USER: str = os.getenv("POSTGRES_USER") or self._raise_missing_env("POSTGRES_USER")
        self.POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD") or self._raise_missing_env("POSTGRES_PASSWORD")
        self.POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER") or self._raise_missing_env("POSTGRES_SERVER")
        self.POSTGRES_PORT: str = os.getenv("POSTGRES_PORT") or self._raise_missing_env("POSTGRES_PORT")
        self.POSTGRES_DB: str = os.getenv("POSTGRES_DB") or self._raise_missing_env("POSTGRES_DB")
        self.POSTGRES_TEST_DB: str = os.getenv("POSTGRES_TEST_DB") or self._raise_missing_env("POSTGRES_TEST_DB")
        self.DATABASE_URL: str = f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        self.TEST_DATABASE_URL: str = f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_TEST_DB}"
        
        self.JWT_SECRET: str = os.getenv("JWT_SECRET") or self._raise_missing_env("JWT_SECRET")
        self.JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM") or self._raise_missing_env("JWT_ALGORITHM")
        self.JWT_REFRESH_SECRET_KEY: str = os.getenv("JWT_REFRESH_SECRET_KEY") or self._raise_missing_env("JWT_REFRESH_SECRET_KEY")
        self.ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # in mins

    def _raise_missing_env(self, env_variable):
        raise ValueError(f"{env_variable} is not set")
    
settings = Settings()