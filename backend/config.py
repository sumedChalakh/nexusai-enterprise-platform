from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    app_name: str = "NexusAI"
    debug: bool = False

    # database
    db_url: str = "postgresql://nexusai:nexusai123@postgres:5432/nexusai"

    # redis
    redis_url: str = "redis://redis:6379"

    # cors
    cors_origins: List[str] = ["http://localhost:3000"]

    # jwt — MUST be set in .env for production
    jwt_secret: str = "change-this-in-production-use-32-chars-minimum"

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


settings = Settings()
