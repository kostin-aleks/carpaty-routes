from typing import Annotated
from slugify import slugify

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlmodel import Session, select
from app.models.mountains import (
    GeoPoint, Ridge, RidgeOut, RidgeCreate, RidgeInfoLink,
    RidgeInfoLinkCreate, Peak, PeakOut, PeakCreate, PeakPhoto,
    Route, RouteOut, RouteCreate, RoutePoint, RoutePhoto,
    RouteSection, RouteSectionCreate, RoutePointCreate)
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


@router.post("/ridge/{ridge_id}/add/link", response_model=RidgeInfoLink)
async def add_ridge_infolink(
        ridge_id: int, infolink: RidgeInfoLinkCreate,
        current_user: Annotated[APIUser, Depends(get_current_active_user)],
        session: Session = Depends(get_session)) -> RidgeInfoLink:
    statement = select(Ridge).where(Ridge.id == ridge_id)
    ridge = session.exec(statement).first()
    if not ridge:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ridge not found")

    db_link = RidgeInfoLink(
        ridge_id=ridge.id,
        link=ridge.link,
        description=ridge.description,
    )

    session.add(db_link)
    session.commit()
    session.refresh(db_link)
    return db_link


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


@router.post("/peaks/add", response_model=Peak)
async def add_peak(
        peak: PeakCreate,
        current_user: Annotated[APIUser, Depends(get_current_active_user)],
        session: Session = Depends(get_session)) -> Peak:
    point_id = None
    if peak.point:
        db_point = GeoPoint(
            latitude=peak.point.latitude,
            longitude=peak.point.longitude,
        )
        session.add(db_point)
        session.commit()
        session.refresh(db_point)
        point_id = db_point.id

    db_peak = Peak(
        name=peak.name,
        description=peak.description,
        slug=slugify(peak.name),
        ridge_id=peak.ridge_id,
        height=peak.height,
        point_id=point_id
    )

    session.add(db_peak)
    session.commit()
    session.refresh(db_peak)
    return db_peak


@router.post("/peak/{peak_id}/add/photo", response_model=PeakPhoto)
async def add_peak_photo(
        peak_id: int, file: UploadFile, description: str | None,
        current_user: Annotated[APIUser, Depends(get_current_active_user)],
        session: Session = Depends(get_session)) -> PeakPhoto:
    statement = select(Peak).where(Peak.id == peak_id)
    peak = session.exec(statement).first()
    if not peak:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Peak not found")

    image_dir = Peak.path_to_images()
    try:
        file_path = f"{image_dir}/{file.filename}"
        with open(file_path, 'wb') as f:
            f.write(file.file.read())
            # return {'message': 'File saved successfully', 'success': True}
        _path = Peak.db_path_to_images()
        photo_path = f'{_path}/{file.filename}'
        image = PeakPhoto(
            peak_id=peak_id,
            photo=photo_path,
            description=description)

        session.add(image)
        session.commit()
        session.refresh(image)

        return image

    except Exception as e:
        return {'message': e.args, 'success': False}


@router.put("/peak/{peak_id}", response_model=Peak)
async def update_peak(
        peak_id: int, peak: PeakCreate,
        current_user: Annotated[APIUser, Depends(get_current_active_user)],
        session: Session = Depends(get_session)) -> Peak:
    statement = select(Peak).where(Peak.id == peak_id)
    db_peak = session.exec(statement).first()
    if not db_peak:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Peak not found")

    db_peak.name = peak.name
    db_peak.description = peak.description
    db_peak.ridge_id = peak.ridge_id
    db_peak.height = peak.height

    point_id = None
    if peak.point:
        db_point = GeoPoint(
            latitude=peak.point.latitude,
            longitude=peak.point.longitude,
        )
        session.add(db_point)
        session.commit()
        session.refresh(db_point)
        point_id = db_point.id
    db_peak.point_id = point_id

    session.add(db_peak)
    session.commit()
    session.refresh(db_peak)

    return db_peak


@router.put("/peak/{peak_id}/photo", response_model=Peak)
async def update_peak_photo(
        peak_id: int, file: UploadFile,
        current_user: Annotated[APIUser, Depends(get_current_active_user)],
        session: Session = Depends(get_session)) -> Peak:
    statement = select(Peak).where(Peak.id == peak_id)
    peak = session.exec(statement).first()
    if not peak:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Peak not found")

    image_dir = Peak.path_to_images()
    try:
        file_path = f"{image_dir}/{file.filename}"
        with open(file_path, 'wb') as f:
            f.write(file.file.read())

        _path = Peak.db_path_to_images()
        photo_path = f'{_path}/{file.filename}'
        peak.photo = photo_path

        session.add(peak)
        session.commit()
        session.refresh(peak)

        return peak

    except Exception as e:
        return {'message': e.args, 'success': False}


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


@router.post("/routes/add", response_model=Route)
async def add_route(
        route: RouteCreate,
        current_user: Annotated[APIUser, Depends(get_current_active_user)],
        session: Session = Depends(get_session)) -> Route:

    db_route = Route(
        name=route.name,
        description=route.description,
        short_description=route.short_description,
        recommended_equipment=route.recommended_equipment,
        slug=slugify(route.name),
        peak_id=route.peak_id,
        difficulty=route.difficulty,
        max_difficulty=route.max_difficulty,
        author=route.author,
        length=route.length,
        year=route.year,
        height_difference=route.height_difference,
        start_height=route.start_height,
        descent=route.descent
    )

    session.add(db_route)
    session.commit()
    session.refresh(db_route)
    return db_route


@router.post("/routes/add/section", response_model=RouteSection)
async def add_route_sction(
        section: RouteSectionCreate,
        current_user: Annotated[APIUser, Depends(get_current_active_user)],
        session: Session = Depends(get_session)) -> RouteSection:

    db_section = RouteSection(
        num=section.num,
        description=section.description,
        route_id=section.route_id,
        difficulty=section.difficulty,
        angle=section.angle,
        length=section.length,
    )

    session.add(db_section)
    session.commit()
    session.refresh(db_section)
    return db_section


@router.post("/routes/add/point", response_model=RoutePoint)
async def add_route_point(
        point: RoutePointCreate,
        current_user: Annotated[APIUser, Depends(get_current_active_user)],
        session: Session = Depends(get_session)) -> RoutePoint:
    point_id = None
    if point.point:
        db_point = GeoPoint(
            latitude=point.point.latitude,
            longitude=point.point.longitude,
        )
        session.add(db_point)
        session.commit()
        session.refresh(db_point)
        point_id = db_point.id

    db_point = RoutePoint(
        description=point.description,
        route_id=point.route_id,
        point_id=point_id,
    )

    session.add(db_point)
    session.commit()
    session.refresh(db_point)
    return db_point


@router.post("/route/{route_id}/add/photo", response_model=RoutePhoto)
async def add_route_photo(
        route_id: int, file: UploadFile, description: str | None,
        current_user: Annotated[APIUser, Depends(get_current_active_user)],
        session: Session = Depends(get_session)) -> RoutePhoto:
    statement = select(Route).where(Route.id == route_id)
    route = session.exec(statement).first()
    if not route:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route not found")

    image_dir = Route.path_to_images()
    try:
        file_path = f"{image_dir}/{file.filename}"
        with open(file_path, 'wb') as f:
            f.write(file.file.read())

        _path = Route.db_path_to_images()
        photo_path = f'{_path}/{file.filename}'
        image = RoutePhoto(
            route_id=route_id,
            photo=photo_path,
            description=description)

        session.add(image)
        session.commit()
        session.refresh(image)

        return image

    except Exception as e:
        return {'message': e.args, 'success': False}


@router.put("/route/{route_id}/map", response_model=Route)
async def update_route_map(
        route_id: int, file: UploadFile,
        current_user: Annotated[APIUser, Depends(get_current_active_user)],
        session: Session = Depends(get_session)) -> Route:
    statement = select(Route).where(Route.id == route_id)
    route = session.exec(statement).first()
    if not route:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route not found")

    image_dir = Route.path_to_images()
    try:
        file_path = f"{image_dir}/{file.filename}"
        with open(file_path, 'wb') as f:
            f.write(file.file.read())

        _path = Route.db_path_to_images()
        photo_path = f'{_path}/{file.filename}'
        route.map_image = photo_path

        session.add(route)
        session.commit()
        session.refresh(route)

        return route

    except Exception as e:
        return {'message': e.args, 'success': False}


@router.put("/route/{route_id}/photo", response_model=Route)
async def update_route_photo(
        route_id: int, file: UploadFile,
        current_user: Annotated[APIUser, Depends(get_current_active_user)],
        session: Session = Depends(get_session)) -> Peak:
    statement = select(Route).where(Route.id == route_id)
    route = session.exec(statement).first()
    if not route:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route not found")

    image_dir = Route.path_to_images()
    try:
        file_path = f"{image_dir}/{file.filename}"
        with open(file_path, 'wb') as f:
            f.write(file.file.read())

        _path = Route.db_path_to_images()
        photo_path = f'{_path}/{file.filename}'
        route.photo = photo_path

        session.add(route)
        session.commit()
        session.refresh(route)

        return route

    except Exception as e:
        return {'message': e.args, 'success': False}


@router.put("/route/{route_id}", response_model=Route)
async def update_route(
        route_id: int, route: RouteCreate,
        current_user: Annotated[APIUser, Depends(get_current_active_user)],
        session: Session = Depends(get_session)) -> Route:
    statement = select(Route).where(Route.id == route_id)
    db_route = session.exec(statement).first()
    if not db_route:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route not found")

    db_route.name = route.name
    db_route.description = route.description
    db_route.short_description = route.short_description
    db_route.recommended_equipment = route.recommended_equipment
    db_route.difficulty = route.difficulty
    db_route.max_difficulty = route.max_difficulty
    db_route.author = route.author
    db_route.length = route.length
    db_route.year = route.year
    db_route.height_difference = route.height_difference
    db_route.start_height = route.start_height
    b_route.descent = route.descent

    session.add(db_route)
    session.commit()
    session.refresh(db_route)

    return db_route


@router.put("/route/section/{section_id}", response_model=RouteSection)
async def update_route_section(
        section_id: int, section: RouteSectionCreate,
        current_user: Annotated[APIUser, Depends(get_current_active_user)],
        session: Session = Depends(get_session)) -> RouteSection:
    statement = select(RouteSection).where(RouteSection.id == section_id)
    db_section = session.exec(statement).first()
    if not db_section:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route section not found")

    db_section.num = section.num
    db_section.description = section.description
    db_section.length = section.length
    db_section.difficulty = section.difficulty
    db_section.angle = section.angle

    session.add(db_section)
    session.commit()
    session.refresh(db_section)

    return db_section
