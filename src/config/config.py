from pydantic import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Finance Dashboard API"
    secret_key: str = "change-me-in-production-use-openssl-rand-hex-32"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24
    database_url: str = "postgresql://postgres:postgres@localhost:5432/finance_db"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
