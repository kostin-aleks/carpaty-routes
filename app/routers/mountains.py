from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.models.mountains import GeoPoint, Ridge, RidgeOut, Peak, Route
from app.database import get_session

# router = APIRouter()

router = APIRouter(
    prefix="/mountains",
    tags=["mountains"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)


# @router.get("/points")
# async def get_points(session: Session = Depends(get_session)):
#     points = session.exec(select(GeoPoint)).all()
#     return points


@router.get("/ridges")
async def get_ridges(session: Session = Depends(get_session)) -> list[Ridge]:
    ridges = session.exec(select(Ridge)).all()
    return ridges


@router.get("/ridge/{slug}")
async def get_ridge(slug: str, session: Session = Depends(get_session)) -> RidgeOut:
    statement = select(Ridge).where(Ridge.slug == slug)
    ridge = session.exec(statement).first()
    if ridge is None:
        raise HTTPException(status_code=404, detail="Ridge not found")
    ridge_out = RidgeOut.from_orm(ridge)

    return ridge_out


@router.get("/peaks")
async def get_peaks(session: Session = Depends(get_session)):
    peaks = session.exec(select(Peak)).all()
    return peaks


@router.get("/routes")
async def get_routes(session: Session = Depends(get_session)):
    routes = session.exec(select(Route)).all()
    return routes
