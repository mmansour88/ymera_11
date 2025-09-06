from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "YMERA 24-Phases"
    DB_URL: str = "sqlite:///./ymera.db"
    JWT_SECRET: str = "change-me"
    JWT_ALG: str = "HS256"
    ACCESS_TTL: int = 3600
    REFRESH_TTL: int = 86400
    CORS_ORIGINS: str = "*"
    FEATURE_MULTIMODAL: bool = True
    FEATURE_MARKETPLACE: bool = True
    FEATURE_FEDERATION: bool = True
    FEATURE_EMOTION: bool = True
    FEATURE_OPTIMIZE: bool = True
    FEATURE_FORECAST: bool = True
    FEATURE_TRUST_LEDGER: bool = True

settings = Settings()
DB_URL = settings.DB_URL

ICE_SERVERS_JSON: str = "[]"  # set to JSON array of RTCIceServer objects via env
