"""
конфигурация соединения с базой данных
"""
from sqlmodel import Session, create_engine

from .settings import config

# Database configurations
_USER = config("DB_USER", cast=str)
_PASSWORD = config("DB_PASSWORD", cast=str)
_HOST = config("DB_HOST", cast=str)
_DATABASE = config("DB_NAME", cast=str)
_PORT = config("DB_PORT", cast=int, default=3306)

MYSQL_DATABASE_URL = f"mysql+pymysql://{_USER}:{_PASSWORD}@{_HOST}:{_PORT}/{_DATABASE}"
db = create_engine(MYSQL_DATABASE_URL, echo=True)  # echo=True for logging SQL queries


def get_session():
    """
    get db session
    """
    with Session(db) as session:
        yield session
