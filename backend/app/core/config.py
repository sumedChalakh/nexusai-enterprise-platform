from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App
    APP_NAME: str = "NexusAI"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "postgresql://nexus:nexus@db:5432/nexusai"

    # JWT
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # AWS S3
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "ap-south-1"
    S3_BUCKET: str = "nexusai-documents"

    # Day 6: Gemini embeddings
    GEMINI_API_KEY: str = ""

    # Day 6: Qdrant vector DB
    QDRANT_HOST: str = "qdrant"
    QDRANT_PORT: int = 6333

    class Config:
        env_file = ".env"


settings = Settings()
