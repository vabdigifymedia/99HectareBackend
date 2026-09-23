from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    DATABASE_URL: str
    APP_NAME: str = "Real Estate API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    REDIS_URL: str

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    ENVIRONMENT: str = "development"
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"

    @property
    def cors_origins_list(self) -> list[str]:
        if not self.CORS_ORIGINS:
            return ["*"]
        origins = [orig.strip() for orig in self.CORS_ORIGINS.split(",") if orig.strip()]
        dev_origins = ["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5173", "http://127.0.0.1:5173"]
        for d in dev_origins:
            if d not in origins:
                origins.append(d)
        return origins

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )



settings = Settings()