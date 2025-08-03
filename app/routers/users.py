from datetime import datetime, timedelta, timezone
import jwt
from typing import Annotated

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from starlette.config import Config
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.models.users import (
    Token, TokenData, User, UserInDB, APIUser, UserCreate, UserUpdate)
from app.database import get_session, db

fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": False,
    }
}


config = Config('.env')

_secret_key = config('SECRET_KEY', cast=str)
_algorithm = config('ALGORITHM', cast=str)
_access_token_expire_minutes = config('ACCESS_TOKEN_EXPIRE_MINUTES', cast=int)


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/token")

router = APIRouter(
    prefix="/users",
    tags=["users"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(username: str):
    session = Session(db)
    statement = select(APIUser).where(APIUser.username == username)
    db_user = session.exec(statement).first()

    return db_user if db_user else None


def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, _secret_key, algorithm=_algorithm)
    return encoded_jwt


async def get_current_user(
        token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, _secret_key, algorithms=[_algorithm])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception

    user = get_user(username=token_data.username)
    print(user, type(user))
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
        current_user: Annotated[APIUser, Depends(get_current_user)]):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@router.post("/token")
async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],) -> Token:
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=_access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@router.get("/me/", response_model=APIUser)
async def read_users_me(
        current_user: Annotated[APIUser, Depends(get_current_active_user)]):
    return current_user


@router.get("/me/items/")
async def read_own_items(
        current_user: Annotated[APIUser, Depends(get_current_active_user)]):
    return [{"item_id": "Foo", "owner": current_user.username}]


@router.post("/register/", response_model=APIUser)
async def register_user(user: UserCreate, session: Session = Depends(get_session)) -> APIUser:
    # Check for existing user
    statement = select(APIUser).where(APIUser.username == user.username)
    db_user = session.exec(statement).first()
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")

    statement = select(APIUser).where(APIUser.email == user.email)
    db_user = session.exec(statement).first()
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    hashed_password = get_password_hash(user.password)
    db_user = APIUser(
        username=user.username,
        email=user.email,
        password=hashed_password,
        first_name=user.first_name,
        last_name=user.last_name,
        middle_name=user.middle_name
    )

    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@router.put("/update/{id}", response_model=APIUser)
async def update_user(
        id: int, user: UserUpdate,
        current_user: Annotated[APIUser, Depends(get_current_active_user)],
        session: Session = Depends(get_session)) -> APIUser:
    # Check for existing user
    statement = select(APIUser).where(APIUser.id == id)
    db_user = session.exec(statement).first()
    if not db_user or db_user.username != user.username:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User not found")

    db_user.first_name = user.first_name
    db_user.last_name = user.last_name
    db_user.middle_name = user.middle_name
    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return(db_user)
