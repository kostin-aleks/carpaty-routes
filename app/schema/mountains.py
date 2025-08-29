"""
Mountain Models
"""

import os
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, HttpUrl
from sqlmodel import Field

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class ResponceStatus(BaseModel):
    """
    Data Model for Status
    """

    message: str = ""
    status: bool = True


class GeoPointCreate(BaseModel):
    """
    Data Model for new Point
    """

    latitude: float = 0
    longitude: float = 0


class GeoPoint(BaseModel):
    """
    Data Model for GeoPoint
    """

    latitude: float = 0
    longitude: float = 0


class RidgeListItem(BaseModel):
    """
    Ridge model for list item
    """

    model_config = ConfigDict(from_attributes=True)
    id: int | None
    slug: str | None
    name: str = Field(max_length=128)


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
    can_be_deleted: bool

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
    can_be_deleted: bool


class RidgeCreate(BaseModel):
    """
    Data Model for new Ridge
    """

    name: str = Field(max_length=128)
    description: Optional[str] = None


class RidgeInfoLinkCreate(BaseModel):
    """
    Data Model for new Link
    """

    ridge_id: Optional[int] = Field(default=None, foreign_key="ridge.id")
    link: HttpUrl = Field(max_length=128)
    description: Optional[str] = None


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
    photo_url: str | None
    editor_id: int | None
    active: bool
    changed: datetime
    can_be_deleted: bool

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
    can_be_deleted: bool


class PeakCreate(BaseModel):
    """
    Data Model for new Peak
    """

    name: str = Field(max_length=128)
    description: Optional[str] = None
    ridge_id: int
    height: Optional[int] = None
    point: Optional[GeoPointCreate] = None


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
    photo_url: str | None
    map_image_url: str | None
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
    can_be_deleted: bool

    photos_list: list
    routepoints_list: list
    sections_list: list


class RouteCreate(BaseModel):
    """
    Data Model for new Route
    """

    peak_id: int
    name: str = Field(max_length=64)
    description: Optional[str] = None
    short_description: Optional[str] = None
    recommended_equipment: Optional[str] = None
    difficulty: str = Field(max_length=3)
    max_difficulty: str = Field(max_length=16)
    author: Optional[str] = None
    length: Optional[int] = None
    year: Optional[int] = None
    height_difference: Optional[int] = None
    start_height: Optional[int] = None
    descent: Optional[str] = None


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
    can_be_deleted: bool


class RouteSectionCreate(BaseModel):
    """
    Data Model for new Route Section
    """

    route_id: int
    num: Optional[int] = None
    description: Optional[str] = None
    length: Optional[int] = None
    difficulty: Optional[str] = None
    angle: Optional[str] = None


class RoutePointCreate(BaseModel):
    """
    Data Model for new Route Point
    """

    route_id: int
    description: Optional[str] = None
    point: GeoPointCreate
