"""
User Models
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from pydantic import EmailStr


class UserData(BaseModel):
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


class UserOut(BaseModel):
    """
    Model for User
    """

    model_config = ConfigDict(from_attributes=True)
    username: str
    email: str
    first_name: str | None
    last_name: str | None
    middle_name: str | None
    is_admin: bool
    is_editor: bool
    is_active: bool
    date_joined: datetime


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
