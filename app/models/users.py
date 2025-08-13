"""
User Models
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr
from sqlmodel import Field, SQLModel


class APIUser(SQLModel, table=True):
    """
    Model for User
    """
    __tablename__ = "api_user"
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(max_length=128, unique=True, index=True)
    email: str = Field(max_length=255, unique=True, index=True)
    first_name: str | None = Field(default=None, max_length=128)
    last_name: str | None = Field(default=None, max_length=128)
    middle_name: str | None = Field(default=None, max_length=128)
    password: str = Field(max_length=128)
    is_admin: bool = Field(default=False)
    is_editor: bool = Field(default=False)
    is_active: bool = Field(default=False)
    date_joined: datetime = Field(default_factory=datetime.utcnow)


#     ridges: List["Ridge"] = Relationship(back_populates="user")
#     peaks: List["Peak"] = Relationship(back_populates="user")
#     routes: List["Route"] = Relationship(back_populates="user")


class UserCreate(BaseModel):
    """
    Input data for new User
    """
    username: str
    email: EmailStr
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    middle_name: Optional[str] = None


class UserUpdate(BaseModel):
    """
    Input data to update User
    """
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    middle_name: Optional[str] = None


class UserEmailUpdate(BaseModel):
    """
    Input data to update User email
    """
    username: str
    email: EmailStr
    new_email: EmailStr


class UserPasswordUpdate(BaseModel):
    """
    Input data to update User password
    """
    username: str
    password: str
    new_password: str


class UserPermission(BaseModel):
    """
    Input data to update User permissions
    """
    is_admin: Optional[bool] = False
    is_editor: bool


class Token(BaseModel):
    """
    data model for token
    """
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """
    token data
    """
    username: str | None = None


# class User(BaseModel):
#     username: str
#     email: str | None = None
#     full_name: str | None = None
#     disabled: bool | None = None


# class UserInDB(User):
#     hashed_password: str
