from pydantic import field_validator, Field
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    app_name: str = "NexusAI"
    debug: bool = False

    @field_validator("debug", mode="before")
    @classmethod
    def parse_debug(cls, value):
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"release", "prod", "production", "false", "0", "no", "off"}:
                return False
            if normalized in {"dev", "debug", "true", "1", "yes", "on"}:
                return True
        return value

    # database
    db_url: str = Field("postgresql://nexusai:nexusai123@postgres:5432/nexusai", validation_alias="database_url")

    # redis
    redis_url: str = "redis://redis:6379"

    # qdrant
    qdrant_host: str = "qdrant"
    qdrant_port: int = 6333
    qdrant_collection: str = "nexusai_chunks"

    # cors
    cors_origins: List[str] = ["http://localhost:3000"]

    # jwt — MUST be set in .env for production
    jwt_secret: str = Field("change-this-in-production-use-32-chars-minimum", validation_alias="secret_key")
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    # gemini
    gemini_api_key: str = ""

    # aws
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_region: str = "ap-south-1"
    s3_bucket: str = "nexusai-docs"

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"


settings = Settings()
