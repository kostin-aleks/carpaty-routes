from datetime import datetime


from fastapi import Depends, FastAPI, HTTPException, status


from pydantic import (
    HttpUrl, field_serializer, computed_field, BaseModel, ConfigDict, EmailStr)
from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy import Column, Text
from sqlalchemy.types import String, TypeDecorator


from typing import Optional, List


class APIUser(SQLModel, table=True):
    __tablename__ = 'api_user'
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(max_length=128, unique=True, index=True)
    email: str = Field(max_length=255, unique=True, index=True)
    first_name: str = Field(default=None, max_length=128)
    last_name: str = Field(default=None, max_length=128)
    middle_name: str = Field(default=None, max_length=128)
    password: str = Field(max_length=128)
    is_admin: bool = Field(default=False)
    is_editor: bool = Field(default=False)
    is_active: bool = Field(default=False)
    date_joined: datetime = Field(default_factory=datetime.utcnow)

#     ridges: List["Ridge"] = Relationship(back_populates="user")
#     peaks: List["Peak"] = Relationship(back_populates="user")
#     routes: List["Route"] = Relationship(back_populates="user")


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    middle_name: str


class UserUpdate(BaseModel):
    username: str
    first_name: str
    last_name: str
    middle_name: str


class UserEmailUpdate(BaseModel):
    username: str
    email: EmailStr
    new_email: EmailStr


class UserPasswordUpdate(BaseModel):
    username: str
    password: str
    new_password: str


class UserPermission(BaseModel):
    is_admin: bool
    is_editor: bool


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None


class UserInDB(User):
    hashed_password: str

