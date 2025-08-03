from typing import Annotated
from slugify import slugify

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.models.mountains import (
    GeoPoint, Ridge, RidgeOut, RidgeCreate, Peak, PeakOut, Route, RouteOut)
from app.models.users import APIUser
from app.database import get_session
from app.routers.users import get_current_active_user


router = APIRouter(
    prefix="/mountains",
    tags=["mountains"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)


@router.get("/ridges")
async def get_ridges(session: Session = Depends(get_session)) -> list[Ridge]:
    ridges = session.exec(select(Ridge)).all()
    return ridges


@router.post("/ridges/add", response_model=Ridge)
async def add_ridge(
        ridge: RidgeCreate,
        current_user: Annotated[APIUser, Depends(get_current_active_user)],
        session: Session = Depends(get_session)) -> Ridge:
    db_ridge = Ridge(
        name=ridge.name,
        description=ridge.description,
        slug=slugify(ridge.name)
    )

    session.add(db_ridge)
    session.commit()
    session.refresh(db_ridge)
    return db_ridge


@router.get("/ridge/{slug}")
async def get_ridge(
        slug: str, session: Session = Depends(get_session)) -> RidgeOut:
    statement = select(Ridge).where(Ridge.slug == slug)
    ridge = session.exec(statement).first()
    if ridge is None:
        raise HTTPException(status_code=404, detail="Ridge not found")
    ridge_out = RidgeOut.from_orm(ridge)

    return ridge_out


@router.get("/peaks")
async def get_peaks(session: Session = Depends(get_session)) -> list[Peak]:
    peaks = session.exec(select(Peak)).all()
    return peaks


@router.get("/peak/{slug}")
async def get_peak(slug: str, session: Session = Depends(get_session)) -> PeakOut:
    statement = select(Peak).where(Peak.slug == slug)
    peak = session.exec(statement).first()
    if peak is None:
        raise HTTPException(status_code=404, detail="Peak not found")
    peak_out = PeakOut.from_orm(peak)

    return peak_out


@router.get("/routes")
async def get_routes(session: Session = Depends(get_session)) -> list[Route]:
    routes = session.exec(select(Route)).all()
    return routes


@router.get("/route/{slug}")
async def get_route(slug: str, session: Session = Depends(get_session)) -> RouteOut:
    statement = select(Route).where(Route.slug == slug)
    route = session.exec(statement).first()
    if route is None:
        raise HTTPException(status_code=404, detail="Route '{slug}' not found")
    route_out = RouteOut.from_orm(route)

    return route_out
