from datetime import datetime


from fastapi import Depends, FastAPI, HTTPException, status


from pydantic import (
    HttpUrl, field_serializer, computed_field, BaseModel, ConfigDict, EmailStr)
from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy import Column, Text
from sqlalchemy.types import String, TypeDecorator


from typing import Optional, List


class GeoCity(SQLModel, table=True):
    __tablename__ = 'geo_city'
    id: int | None = Field(default=None, primary_key=True)
    geonameid: int = Field(default=0, index=True)
    name: str | None = Field(max_length=200, default=None)
    asciiname: str | None = Field(default=None, max_length=200)
    alternatenames: str | None = Field(default=None)
    latitude: float | None = Field(default=0)
    longitude: float | None = Field(default=0)
    fclass: str | None = Field(max_length=1)
    fcode: str | None = Field(max_length=10)

    country: str | None = Field(max_length=2, index=True)
    cc2: str | None = Field(max_length=60, index=True)
    admin1: str | None = Field(max_length=20, index=True)
    admin2: str | None = Field(max_length=80)
    admin3: str | None = Field(max_length=20)
    admin4: str | None = Field(max_length=20)
    population: int | None = Field(default=None)
    elevation: int | None = Field(default=None)
    gtopo30: int | None = Field(default=None)
    timezone: str | None = Field(max_length=40)

    moddate: datetime | None = Field(default=None)


class GeoCountry(SQLModel, table=True):
    __tablename__ = 'geo_country'
    id: int | None = Field(default=None, primary_key=True)
    geoname_id: int = Field(default=0, index=True)
    name: str | None = Field(max_length=128, default=None)
    iso: str = Field(max_length=2, index=True)
    capital: str | None = Field(max_length=128, default=None)
    iso3: str = Field(max_length=3, index=True)
    iso_num: int = Field(max_length=3, index=True)
    fips: str | None = Field(max_length=2, default=None)
    area_sqkm: int | None = Field(default=None)
    population: int | None = Field(default=None)
    continent: str = Field(max_length=2)
    tld: str | None = Field(max_length=6, default=None)
    currency_code: str | None = Field(max_length=3, default=None, index=True)
    currency_name: str | None = Field(max_length=32, default=None, index=True)


class GeoCountryLanguage(SQLModel, table=True):
    __tablename__ = 'geo_country_language'
    id: int | None = Field(default=None, primary_key=True)
    country_iso3: str = Field(max_length=3, index=True)
    lang_code: str = Field(max_length=10, index=True)


class GeoCountryNeighbour(SQLModel, table=True):
    __tablename__ = 'geo_country_neighbour'
    id: int | None = Field(default=None, primary_key=True)
    country_iso3: str = Field(max_length=3, index=True)
    neighbour_iso: str = Field(max_length=2, index=True)


class GeoCountryAdminSubject(SQLModel, table=True):
    __tablename__ = 'geo_country_subject'
    id: int | None = Field(default=None, primary_key=True)
    geoname_id: int = Field(default=0, index=True)
    country_iso: str = Field(max_length=2, index=True)
    name: str | None = Field(max_length=128, default=None)
    code: str = Field(max_length=10, index=True)


class GeoRUSSubject(SQLModel, table=True):
    __tablename__ = 'geo_russia_subject'
    id: int | None = Field(default=None, primary_key=True)
    geoname_id: int = Field(default=0, index=True)
    country_iso: str = Field(max_length=2, index=True)
    name: str | None = Field(max_length=128, default=None)
    code: str = Field(max_length=10, index=True)
    ascii_name: str | None = Field(default=None, max_length=128)
    iso_3166_2_code: str = Field(max_length=16, index=True)
    gai_code: str = Field(max_length=32, index=True)


class GeoUKRSubject(SQLModel, table=True):
    __tablename__ = 'geo_ukraine_subject'
    id: int | None = Field(default=None, primary_key=True)
    geoname_id: int = Field(default=0, index=True)
    country_iso: str = Field(max_length=2, index=True)
    name: str | None = Field(max_length=128, default=None)
    code: str = Field(max_length=10, index=True)
    ascii_name: str | None = Field(default=None, max_length=128)
    iso_3166_2_code: str = Field(max_length=16, index=True)
