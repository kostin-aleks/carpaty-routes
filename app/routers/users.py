"""
Router Mountains
"""

from datetime import datetime, timedelta, timezone
from app.dependencies import verify_password, get_password_hash
from typing import Annotated

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from sqlmodel import Session, select
from starlette.config import Config

from app.database import db, get_session
from app.models.users import (
    APIUser,
    Token,
    TokenData,
    UserCreate,
    UserEmailUpdate,
    UserPasswordUpdate,
    UserPermission,
    UserUpdate,
)

config = Config(".env")

_SECRET_KEY = config("SECRET_KEY", cast=str)
_ALGORITHM = config("ALGORITHM", cast=str)
_ACCESS_TOKEN_EXPIRE_MINUTES = config("ACCESS_TOKEN_EXPIRE_MINUTES", cast=int)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/token")

router = APIRouter(
    prefix="/users",
    tags=["users"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)


def get_user(username: str):
    """get user by username"""
    session = Session(db)
    statement = select(APIUser).where(APIUser.username == username)
    db_user = session.exec(statement).first()

    return db_user if db_user else None


def authenticate_user(username: str, password: str):
    """authenticate user"""
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """create access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, _SECRET_KEY, algorithm=_ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    """get current user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, _SECRET_KEY, algorithms=[_ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception

    user = get_user(username=token_data.username)

    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[APIUser, Depends(get_current_user)]
):
    """get current active user"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    """login by username and password and return token"""
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@router.get("/me/", response_model=APIUser)
async def read_users_me(
    current_user: Annotated[APIUser, Depends(get_current_active_user)]
):
    """return data for current user"""
    return current_user


@router.post("/register/", response_model=APIUser)
async def register_user(
    user: UserCreate, session: Session = Depends(get_session)
) -> APIUser:
    """register new user"""
    # Check for existing user
    statement = select(APIUser).where(APIUser.username == user.username)
    db_user = session.exec(statement).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    statement = select(APIUser).where(APIUser.email == user.email)
    db_user = session.exec(statement).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    hashed_password = get_password_hash(user.password)
    db_user = APIUser(
        username=user.username,
        email=user.email,
        password=hashed_password,
        first_name=user.first_name,
        last_name=user.last_name,
        middle_name=user.middle_name,
    )

    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@router.put("/update/{user_id}", response_model=APIUser)
async def update_user(
    user_id: int,
    user: UserUpdate,
    current_user: Annotated[APIUser, Depends(get_current_active_user)],
    session: Session = Depends(get_session),
) -> APIUser:
    """update user"""
    # Check for existing user
    statement = select(APIUser).where(APIUser.id == user_id)
    db_user = session.exec(statement).first()
    if not db_user or db_user.username != user.username:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    user_dict = user.model_dump(exclude_unset=True)
    for key, value in user_dict.items():
        setattr(db_user, key, value)

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user


@router.put("/set/permissions/{user_id}", response_model=APIUser)
async def set_user_permissions(
    user_id: int,
    data: UserPermission,
    current_user: Annotated[APIUser, Depends(get_current_active_user)],
    session: Session = Depends(get_session),
) -> APIUser:
    """update user permissions"""
    # Check for existing user
    statement = select(APIUser).where(APIUser.id == user_id)
    db_user = session.exec(statement).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    # check permission
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No permission for this action",
        )

    data_dict = data.model_dump(exclude_unset=True)
    for key, value in data_dict.items():
        setattr(db_user, key, value)

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user


@router.put("/email/update", response_model=APIUser)
async def update_user_email(
    user: UserEmailUpdate,
    current_user: Annotated[APIUser, Depends(get_current_active_user)],
    session: Session = Depends(get_session),
) -> APIUser:
    """update user email"""
    # Check for existing user
    statement = select(APIUser).where(APIUser.email == user.email)
    db_user = session.exec(statement).first()
    if not db_user or db_user.username != user.username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User not found"
        )

    db_user.email = user.new_email
    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user


@router.put("/password/update", response_model=APIUser)
async def update_user_password(
    user: UserPasswordUpdate,
    current_user: Annotated[APIUser, Depends(get_current_active_user)],
    session: Session = Depends(get_session),
) -> APIUser:
    """update user password"""
    # Check for existing user
    statement = select(APIUser).where(APIUser.username == user.username)
    db_user = session.exec(statement).first()
    if not (db_user and verify_password(user.password, db_user.password)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User not found"
        )

    db_user.password = get_password_hash(user.new_password)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user
