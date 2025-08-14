"""
Dependencies
"""

from passlib.context import CryptContext
from sqlmodel import Session, create_engine
from starlette.config import Config

config = Config(".env")

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


# from starlette.config import Config

# config = Config(".env")

# _SECRET_KEY = config("SECRET_KEY", cast=str)
# _ALGORITHM = config("ALGORITHM", cast=str)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    """verify password"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    """create and return hash of password"""
    return pwd_context.hash(password)
