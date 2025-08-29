"""
User Models
"""

from datetime import datetime

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
