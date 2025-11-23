import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    SECRET_KEY: str
    OPENAI_API_KEY: str
    UPLOAD_FOLDER: str = "./uploads"
    MAX_CONTENT_LENGTH: int = 16*1024*1024
    ALLOWED_EXTENSIONS: set[str] = set()
    PORT: int = 5000
    DEBUG: bool
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    RABBITMQ_USER: str
    RABBITMQ_PASS: str
    RABBITMQ_VHOST: str
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str
    USE_TEST_DATABASE: bool
    DB_HOST: str
    DB_PORT: int = 5432
    POSTGRES_ROOT_USER: str
    POSTGRES_ROOT_PASSWORD: str
    DB_USER: str
    DB_PASS: str
    DB_NAME: str
    TEST_DB_USER: str
    TEST_DB_NAME: str
    TEST_DB_PASS: str

    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GITHUB_CLIENT_ID: str
    GITHUB_CLIENT_SECRET: str
    LINKEDIN_CLIENT_ID: str
    LINKEDIN_CLIENT_SECRET: str

    JWT_ALGORITHM: str
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int

    FLASK_ENV: str = "development"

    @property
    def DATABASE_URL_psycopg(self):
        return f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def TEST_DATABASE_URL_psycopg(self):
        return f"postgresql+psycopg2://{self.TEST_DB_USER}:{self.TEST_DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.TEST_DB_NAME}"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Ensure upload directory exists
    def __init__(self, **values):
        super().__init__(**values)
        os.makedirs(self.UPLOAD_FOLDER, exist_ok=True)


settings = Settings()
