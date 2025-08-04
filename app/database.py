from sqlmodel import create_engine
# from starlette.config import Config
from sqlmodel import Session

from .settings import config

# config = Config('.env')

# Database configurations
_user = config('DB_USER', cast=str)
_password = config('DB_PASSWORD', cast=str)
_host = config('DB_HOST', cast=str)
_database = config('DB_NAME', cast=str)
_port = config('DB_PORT', cast=int, default=3306)

MYSQL_DATABASE_URL = f"mysql+pymysql://{_user}:{_password}@{_host}:{_port}/{_database}"
db = create_engine(MYSQL_DATABASE_URL, echo=True)  # echo=True for logging SQL queries


def get_session():
    with Session(db) as session:
        yield session
