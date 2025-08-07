import typing as tp
import uuid

import bcrypt
from sqlalchemy import Boolean, Integer, String, Text, select, update
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from fastadmin import SqlAlchemyModelAdmin, register

from app.database import MYSQL_DATABASE_URL, db
from app.models.users import APIUser

sqlalchemy_sessionmaker = async_sessionmaker(db, expire_on_commit=False)


@register(APIUser, sqlalchemy_sessionmaker=sqlalchemy_sessionmaker)
class APIUserAdmin(SqlAlchemyModelAdmin):
    exclude = ("password",)
    list_display = ("id", "username", "is_admin", "is_active", "is_editor")
    list_display_links = ("id", "username")
    list_filter = ("id", "username", "is_admin", "is_active", "is_editor")
    search_fields = ("username",)


