import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    def __init__(self):
        self.DATABASE_URL: str = os.getenv("DATABASE_URL") or self._raise_missing_env("DATABASE_URL")
        self.TEST_DATABASE_URL: str = os.getenv("TEST_DATABASE_URL") or self._raise_missing_env("TEST_DATABASE_URL")
        
        self.JWT_SECRET: str = os.getenv("JWT_SECRET") or self._raise_missing_env("JWT_SECRET")
        self.JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM") or self._raise_missing_env("JWT_ALGORITHM")
        self.JWT_REFRESH_SECRET_KEY: str = os.getenv("JWT_REFRESH_SECRET_KEY") or self._raise_missing_env("JWT_REFRESH_SECRET_KEY")
        self.ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # in mins

    def _raise_missing_env(self, env_variable):
        raise ValueError(f"{env_variable} is not set")
    
settings = Settings()