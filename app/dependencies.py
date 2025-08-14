"""
Dependencies
"""

from passlib.context import CryptContext

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
