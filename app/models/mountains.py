from datetime import datetime
import os

from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy import Column, Text
from sqlalchemy.types import String, TypeDecorator
from pydantic import HttpUrl, field_serializer, computed_field, BaseModel, ConfigDict
from typing import Optional, List

import app.settings as app_settings
from app.models.users import APIUser

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class MediaRoot:
    @staticmethod
    def root():
        media_root = f'{PROJECT_ROOT}{app_settings.MEDIA_ROOT}'
        photos_root = f'{media_root}{app_settings.PHOTOS_ROOT}'
        try:
            os.makedirs(photos_root, exist_ok=True)
            print(f"Folder '{photos_root}' created successfully or already existed.")
        except OSError as e:
            print(f"Error creating folder '{photos_root}': {e}")

        return photos_root

    @staticmethod
    def path_to_images(Cls):
        media_root = MediaRoot.root()
        _now = datetime.now().strftime("%Y%m%d%H%M")
        _directory = f'{media_root}/{Cls.__name__.lower()}/{_now}'
        try:
            os.makedirs(_directory, exist_ok=True)
            print(f"Folder '{_directory}' created successfully or already existed.")
        except OSError as e:
            print(f"Error creating folder '{_directory}': {e}")

        return _directory

    @staticmethod
    def db_path_to_images(Cls):
        _now = datetime.now().strftime("%Y%m%d%H%M")
        _directory = f'{app_settings.PHOTOS_ROOT}/{Cls.__name__.lower()}/{_now}'
        return _directory


class HttpUrlType(TypeDecorator):
    impl = String(2083)
    cache_ok = True
    python_type = HttpUrl

    def process_bind_param(self, value, dialect) -> str:
        return str(value)

    def process_result_value(self, value, dialect) -> HttpUrl:
        return HttpUrl(url=value)

    def process_literal_param(self, value, dialect) -> str:
        return str(value)


class GeoPoint(SQLModel, table=True):
    __tablename__ = 'geopoint'
    id: int | None = Field(default=None, primary_key=True)
    latitude: float = 0
    longitude: float = 0

    peaks: List["Peak"] = Relationship(back_populates="point")
    routepoints: List["RoutePoint"] = Relationship(back_populates="point")


class ResponceStatus(BaseModel):
    message: str = ''
    status: bool = True


class GeoPointCreate(BaseModel):
    latitude: float = 0
    longitude: float = 0


class Ridge(SQLModel, table=True):
    """
    Ridge model
    """
    __tablename__ = 'ridge'
    id: int | None = Field(default=None, primary_key=True)
    slug: str | None = Field(default=None, unique=True, max_length=128)
    name: str = Field(max_length=128)
    description: str | None = Field(default=None, sa_column=Column(Text))
    editor_id: Optional[int] = Field(default=None, foreign_key="api_user.id")
    editor: Optional[APIUser] = Relationship()
    active: bool = Field(default=True)
    changed: datetime = Field(default_factory=datetime.utcnow)

    infolinks: List["RidgeInfoLink"] = Relationship(back_populates="ridge")
    peaks: List["Peak"] = Relationship(back_populates="ridge")

    @computed_field
    @property
    def peaks_list(self) -> list:
        return self.peaks

    @computed_field
    @property
    def infolinks_list(self) -> list:
        return self.infolinks

    @classmethod
    def path_to_images(cls):
        media_root = MediaRoot.root()
        _now = datetime.now().strftime("%Y%m%d%H%M")
        _directory = f'{media_root}/{cls.__name__.lower()}/{_now}'
        try:
            os.makedirs(_directory, exist_ok=True)
            print(f"Folder '{_directory}' created successfully or already existed.")
        except OSError as e:
            print(f"Error creating folder '{_directory}': {e}")

        return _directory


class RidgeOut(BaseModel):
    """
    Ridge model for single Ridge response
    """
    model_config = ConfigDict(from_attributes=True)
    id: int | None
    slug: str | None
    name: str = Field(max_length=128)
    description: str | None
    editor_id: int | None
    active: bool = Field(default=True)
    changed: datetime | None

    peaks_list: list | None = []
    infolinks_list: list | None = []


class RidgeShortOut(BaseModel):
    """
    Ridge model for single Ridge response
    short information
    """
    model_config = ConfigDict(from_attributes=True)
    slug: str | None
    name: str = Field(max_length=128)


class RidgeInfoLink(SQLModel, table=True):
    """
    Ridge Info Link model
    """
    __tablename__ = 'ridge_info_link'
    id: int | None = Field(default=None, primary_key=True)
    ridge_id: Optional[int] = Field(default=None, foreign_key="ridge.id")
    ridge: Optional[Ridge] = Relationship(back_populates="infolinks")
    link: HttpUrl = Field(index=True, unique=True, nullable=False, sa_type=HttpUrlType, max_length=128)
    description: str | None = Field(default=None, max_length=128)


class RidgeCreate(BaseModel):
    name: str = Field(max_length=128)
    description: str


class RidgeInfoLinkCreate(BaseModel):
    ridge_id: Optional[int] = Field(default=None, foreign_key="ridge.id")
    link: HttpUrl = Field(max_length=128)
    description: str | None


class Peak(SQLModel, table=True):
    """
    Peak model
    """
    __tablename__ = 'peak'
    id: int | None = Field(default=None, primary_key=True)
    slug: str | None = Field(default=None, unique=True, max_length=64)
    ridge_id: Optional[int] = Field(default=None, foreign_key="ridge.id")
    ridge: Optional[Ridge] = Relationship(back_populates="peaks")
    name: str = Field(max_length=64)
    description: str | None = Field(default=None, sa_column=Column(Text))
    height: int | None = Field(default=None)
    point_id: Optional[int] = Field(default=None, foreign_key="geopoint.id")
    point: Optional[GeoPoint] = Relationship(back_populates="peaks")
    photo: str | None = Field(default=None, unique=True, max_length=128)
    editor_id: Optional[int] = Field(default=None, foreign_key="api_user.id")
    editor: Optional[APIUser] = Relationship()
    active: bool = Field(default=True)
    changed: datetime = Field(default_factory=datetime.utcnow)

    photos: List["PeakPhoto"] = Relationship(back_populates="peak")
    routes: List["Route"] = Relationship(back_populates="peak")

    @computed_field
    @property
    def photos_list(self) -> list:
        return self.photos

    @computed_field
    @property
    def routes_list(self) -> list:
        return self.routes

    @classmethod
    def path_to_images(cls):
        return MediaRoot.path_to_images(cls)

    @classmethod
    def db_path_to_images(cls):
        return MediaRoot.db_path_to_images(cls)


class PeakOut(BaseModel):
    """
    Peak model for single Peak
    """
    model_config = ConfigDict(from_attributes=True)
    id: int | None
    slug: str | None
    ridge_id: Optional[int]
    ridge: Optional[RidgeShortOut]
    name: str
    description: str | None
    height: int | None
    # point_id: Optional[int]
    point: Optional[GeoPoint]
    photo: str | None
    editor_id: int | None
    active: bool
    changed: datetime

    photos_list: list | None = []
    routes_list: list | None = []


class PeakShortOut(BaseModel):
    """
    Peak model for single Peak
    short information
    """
    model_config = ConfigDict(from_attributes=True)
    id: int | None
    slug: str | None
    name: str
    height: int | None


class PeakCreate(BaseModel):
    name: str = Field(max_length=128)
    description: str
    ridge_id: int
    height: int | None
    point: Optional[GeoPointCreate] | None


class PeakPhoto(SQLModel, table=True):
    """
    Peak Photo model
    """
    __tablename__ = 'peak_photo'
    id: int | None = Field(default=None, primary_key=True)
    peak_id: Optional[int] = Field(default=None, foreign_key="peak.id")
    peak: Optional[Peak] = Relationship(back_populates="photos")
    photo: str | None = Field(default=None, unique=True, max_length=128)
    description: str | None = Field(default=None, max_length=128)


class Route(SQLModel, table=True):
    """
    Route model
    """
    __tablename__ = 'route'
    id: int | None = Field(default=None, primary_key=True)
    peak_id: Optional[int] = Field(default=None, foreign_key="peak.id")
    peak: Optional[Peak] = Relationship(back_populates="routes")
    name: str = Field(max_length=64)
    slug: str | None = Field(default=None, unique=True, max_length=64)
    description: str | None = Field(default=None, sa_column=Column(Text))
    short_description: str | None = Field(default=None, sa_column=Column(Text))
    recommended_equipment: str | None = Field(default=None, sa_column=Column(Text))
    photo: str | None = Field(default=None, unique=True, max_length=128)
    map_image: str | None = Field(default=None, unique=True, max_length=128)
    difficulty: str | None = Field(default=None, max_length=3)
    max_difficulty: str | None = Field(default=None, max_length=16)
    author: str | None = Field(default=None, max_length=64)
    length: int | None = Field(default=None)
    year: int | None = Field(default=None)
    height_difference: int | None = Field(default=None)
    start_height: int | None = Field(default=None)
    descent: str | None = Field(default=None, sa_column=Column(Text))
    editor_id: Optional[int] = Field(default=None, foreign_key="api_user.id")
    editor: Optional[APIUser] = Relationship()
    changed: datetime = Field(default_factory=datetime.utcnow)
    ready: bool = Field(default=False)

    photos: List["RoutePhoto"] = Relationship(back_populates="route")
    routepoints: List["RoutePoint"] = Relationship(back_populates="route")
    sections: List["RouteSection"] = Relationship(back_populates="route")

    @computed_field
    @property
    def photos_list(self) -> list:
        return self.photos

    @computed_field
    @property
    def routepoints_list(self) -> list:
        return self.routepoints

    @computed_field
    @property
    def sections_list(self) -> list:
        return self.sections

    @classmethod
    def path_to_images(cls):
        return MediaRoot.path_to_images(cls)

    @classmethod
    def db_path_to_images(cls):
        return MediaRoot.db_path_to_images(cls)


class RouteOut(BaseModel):
    """
    Route model
    """
    model_config = ConfigDict(from_attributes=True)
    id: int
    peak_id: Optional[int]
    peak: Optional[PeakShortOut]
    name: str
    slug: str | None
    description: str | None
    short_description: str | None
    recommended_equipment: str | None
    photo: str | None
    map_image: str | None
    difficulty: str | None
    max_difficulty: str | None
    author: str | None
    length: int | None
    year: int | None
    height_difference: int | None
    start_height: int | None
    descent: str | None
    editor_id: int | None
    changed: datetime
    ready: bool

    photos_list: list
    routepoints_list: list
    sections_list: list


class RouteCreate(BaseModel):
    peak_id: int
    name: str = Field(max_length=64)
    description: str | None
    short_description: str | None
    recommended_equipment: str | None
    difficulty: str | None = Field(max_length=3)
    max_difficulty: str | None = Field(max_length=16)
    author: str | None = Field(max_length=64)
    length: int | None
    year: int | None
    height_difference: int
    start_height: int | None
    descent: str


class RouteListItem(BaseModel):
    """
    Route model for single Route
    short information
    """
    model_config = ConfigDict(from_attributes=True)
    id: int | None
    slug: str | None
    name: str
    difficulty: str | None = Field(max_length=3)
    max_difficulty: str | None = Field(max_length=16)


class RouteSection(SQLModel, table=True):
    """
    Route Section model
    """
    __tablename__ = 'route_section'
    id: int | None = Field(default=None, primary_key=True)
    route_id: Optional[int] = Field(default=None, foreign_key="route.id")
    route: Optional[Route] = Relationship(back_populates="sections")
    num: int | None = Field(default=None)
    description: str | None = Field(default=None, sa_column=Column(Text))
    length: int | None = Field(default=None)
    difficulty: str | None = Field(default=None, max_length=32)
    angle: str | None = Field(default=None, max_length=32)


class RouteSectionCreate(BaseModel):
    route_id: int
    num: int | None
    description: str | None
    length: int | None
    difficulty: str | None = Field(max_length=32)
    angle: str | None = Field(max_length=32)


class RoutePhoto(SQLModel, table=True):
    """
    Route Photo model
    """
    __tablename__ = 'route_photo'
    id: int | None = Field(default=None, primary_key=True)
    route_id: Optional[int] = Field(default=None, foreign_key="route.id")
    route: Optional[Route] = Relationship(back_populates="photos")
    photo: str | None = Field(default=None, unique=True, max_length=128)
    description: str | None = Field(default=None, max_length=128)


class RoutePoint(SQLModel, table=True):
    """
    Route Point model
    """
    __tablename__ = 'route_point'
    id: int | None = Field(default=None, primary_key=True)
    route_id: Optional[int] = Field(default=None, foreign_key="route.id")
    route: Optional[Route] = Relationship(back_populates="routepoints")
    point_id: Optional[int] = Field(default=None, foreign_key="geopoint.id")
    point: Optional[GeoPoint] = Relationship(back_populates="routepoints")
    description: str | None = Field(default=None, max_length=128)

    @computed_field
    @property
    def latitude(self) -> float:
        return self.point.latitude

    @computed_field
    @property
    def longitude(self) -> float:
        return self.point.longitude


class RoutePointCreate(BaseModel):
    route_id: int
    description: str | None
    point: Optional[GeoPointCreate] | None
