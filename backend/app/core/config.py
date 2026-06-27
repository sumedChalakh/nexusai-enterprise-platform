"""Application settings exposed with both legacy and current names."""
from config import settings as _settings


class SettingsAdapter:
    @property
    def APP_NAME(self) -> str:
        return _settings.app_name

    @property
    def DEBUG(self) -> bool:
        return _settings.debug

    @property
    def DATABASE_URL(self) -> str:
        return _settings.db_url

    @property
    def DB_URL(self) -> str:
        return _settings.db_url

    @property
    def REDIS_URL(self) -> str:
        return _settings.redis_url

    @property
    def SECRET_KEY(self) -> str:
        return _settings.jwt_secret

    @property
    def JWT_SECRET(self) -> str:
        return _settings.jwt_secret

    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    @property
    def GEMINI_API_KEY(self) -> str:
        return _settings.gemini_api_key

    @property
    def QDRANT_HOST(self) -> str:
        return _settings.qdrant_host

    @property
    def QDRANT_PORT(self) -> int:
        return _settings.qdrant_port

    @property
    def QDRANT_COLLECTION(self) -> str:
        return _settings.qdrant_collection

    @property
    def AWS_ACCESS_KEY_ID(self) -> str:
        return _settings.aws_access_key_id

    @property
    def AWS_SECRET_ACCESS_KEY(self) -> str:
        return _settings.aws_secret_access_key

    @property
    def AWS_REGION(self) -> str:
        return _settings.aws_region

    @property
    def S3_BUCKET(self) -> str:
        return _settings.s3_bucket

    def __getattr__(self, name):
        return getattr(_settings, name)


settings = SettingsAdapter()
