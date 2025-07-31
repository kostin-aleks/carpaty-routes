from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.models.mountains import GeoPoint, Ridge
from app.database import get_session

# router = APIRouter()

router = APIRouter(
    prefix="/mountains",
    tags=["mountains"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)


@router.get("/points")
async def get_points(session: Session = Depends(get_session)):
    points = session.exec(select(GeoPoint)).all()
    return points


@router.get("/ridges")
async def get_ridges(session: Session = Depends(get_session)):
    ridges = session.exec(select(Ridge)).all()
    return ridges

# @router.get("/users/me", tags=["users"])
# async def read_user_me():
#     return {"username": "fakecurrentuser"}
#
#
# @router.get("/users/{username}", tags=["users"])
# async def read_user(username: str):
#     return {"username": username}
