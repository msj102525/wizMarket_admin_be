from pydantic import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    ALLOWED_ORIGINS: str

    class Config:
        env_file = ".env"

settings = Settings()
