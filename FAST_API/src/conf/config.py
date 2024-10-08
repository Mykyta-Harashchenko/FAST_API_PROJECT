from pydantic import ConfigDict, field_validator, EmailStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_URL: str = "postgresql+asyncpg://myuser:mysecretpassword@localhost:5432/postgres"
    SECRET_KEY_JWT: str = "1234567890"
    ALGORITHM: str = "HS256"
    MAIL_USERNAME: str = "postgres@mail.com"
    MAIL_PASSWORD: str = "postgres"
    MAIL_FROM: str = "postgres@mail.com"
    MAIL_PORT: int = 465
    MAIL_SERVER: str = "smtp.mail.com"
    REDIS_DOMAIN: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str | None = None
    CLD_NAME: str = "abc"
    CLD_API_KEY: str = "abc123"
    CLD_API_SECRET: str = "secret"

    @field_validator("ALGORITHM")
    @classmethod
    def validate_algorithm(cls, v):
        if v not in ["HS256", "HS512"]:
            raise ValueError("Algorithm must be HS256 or HS512")
        return v

    model_config = ConfigDict(
        extra="ignore", env_file=".env", env_file_encoding="utf-8"
    )


config = Settings()
