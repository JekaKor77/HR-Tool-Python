from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from app_config import settings


DATABASE_URL = settings.TEST_DATABASE_URL_psycopg if settings.USE_TEST_DATABASE else settings.DATABASE_URL_psycopg


sync_engine = create_engine(
    url=DATABASE_URL,
    echo=True,
    pool_size=5,
    max_overflow=10
)

sync_session_factory = sessionmaker(
    sync_engine,
    expire_on_commit=False,
    autoflush=True
)
