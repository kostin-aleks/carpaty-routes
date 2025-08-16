"""
Router Mountains
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, status
from slugify import slugify
from sqlmodel import Session, select

from app.dependencies import db, get_session
from app.i18n import _
from app.models.mountains import (
    GeoPoint,
    Peak,
    PeakCreate,
    PeakOut,
    PeakPhoto,
    PeakShortOut,
    ResponceStatus,
    Ridge,
    RidgeCreate,
    RidgeInfoLink,
    RidgeInfoLinkCreate,
    RidgeOut,
    Route,
    RouteCreate,
    RouteListItem,
    RouteOut,
    RoutePhoto,
    RoutePoint,
    RoutePointCreate,
    RouteSection,
    RouteSectionCreate,
)
from app.models.users import APIUser
from app.routers.users import get_current_active_user

router = APIRouter(
    prefix="/mountains",
    tags=["mountains"],
    responses={404: {"description": _("Not found")}},
)


def unique_slugify(klas, text: str) -> str:
    """slugify string and check that is unique"""
    session = Session(db)
    slug = slugify(text)
    for k in range(100):
        _slug = slug
        if k:
            _slug = f"{slug}-{k}"
        statement = select(klas).where(klas.slug == _slug)
        item = session.exec(statement).first()
        if not item:
            slug = _slug
            break
    return slug


def checked_ridge(session: Session, ridge_id: int = None, slug: str = None) -> Ridge:
    """select and return the ridge by id or slug. Raise 404 if ridge is not found"""
    if ridge_id:
        statement = select(Ridge).where(Ridge.id == ridge_id)
    else:
        statement = select(Ridge).where(Ridge.slug == slug)
    ridge = session.exec(statement).first()
    if not ridge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=_("Ridge not found")
        )
    return ridge


def checked_peak(session: Session, peak_id: int = None, slug: str = None) -> Peak:
    """select and return the peak by id or slug. Raise 404 if peak is not found"""
    if peak_id:
        statement = select(Peak).where(Peak.id == peak_id)
    else:
        statement = select(Peak).where(Peak.slug == slug)
    peak = session.exec(statement).first()
    if not peak:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=_("Peak not found")
        )
    return peak


def checked_route(session: Session, route_id: int = None, slug: str = None) -> Route:
    """select and return the route by id or slug. Raise 404 if route is not found"""
    if route_id:
        statement = select(Route).where(Route.id == route_id)
    else:
        statement = select(Route).where(Route.slug == slug)
    route = session.exec(statement).first()
    if not route:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=_("Route not found")
        )
    return route


def can_add(current_user: APIUser) -> bool:
    """can user add this object"""
    if not (current_user.is_admin or current_user.is_editor):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=_("No permission for this action"),
        )
    return True


def can_edit(current_user: APIUser, obj) -> bool:
    """can user update or delete this object"""
    if not (
        current_user.is_admin or (current_user.is_editor and obj.editor == current_user)
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=_("No permission for this action"),
        )
    return True


@router.get("/ridges")
async def get_ridges(session: Session = Depends(get_session)) -> list[Ridge]:
    """get list of mountain ridges"""
    ridges = session.exec(select(Ridge)).all()
    return ridges


@router.post("/ridges/add", response_model=Ridge)
async def add_ridge(
    ridge: RidgeCreate,
    current_user: Annotated[APIUser, Depends(get_current_active_user)],
    session: Session = Depends(get_session),
) -> Ridge:
    """add new ridge"""
    can_add(current_user)

    db_ridge = Ridge(
        name=ridge.name,
        description=ridge.description,
        editor_id=current_user.id,
        slug=unique_slugify(Ridge, ridge.name),
    )

    session.add(db_ridge)
    session.commit()
    session.refresh(db_ridge)
    return db_ridge


@router.put("/ridge/{slug}", response_model=Ridge)
async def update_ridge(
    slug: str,
    ridge: RidgeCreate,
    current_user: Annotated[APIUser, Depends(get_current_active_user)],
    session: Session = Depends(get_session),
) -> Ridge:
    """update the ridge fields"""
    db_ridge = checked_ridge(session, slug=slug)

    can_edit(current_user)

    ridge_dict = ridge.model_dump(exclude_unset=True)
    for key, value in ridge_dict.items():
        setattr(db_ridge, key, value)

    session.add(db_ridge)
    session.commit()
    session.refresh(db_ridge)

    return db_ridge


@router.get("/ridge/{slug}")
async def get_ridge(slug: str, session: Session = Depends(get_session)) -> RidgeOut:
    """get the ridge by slug"""
    statement = select(Ridge).where(Ridge.slug == slug)
    ridge = session.exec(statement).first()
    if ridge is None:
        raise HTTPException(status_code=404, detail=_("Ridge not found"))
    ridge_out = RidgeOut.model_validate(ridge)

    return ridge_out


@router.post("/ridge/{ridge_id}/add/link", response_model=RidgeInfoLink)
async def add_ridge_infolink(
    ridge_id: int,
    infolink: RidgeInfoLinkCreate,
    current_user: Annotated[APIUser, Depends(get_current_active_user)],
    session: Session = Depends(get_session),
) -> RidgeInfoLink:
    """add new link to the ridge"""
    ridge = checked_ridge(session, ridge_id=ridge_id)

    can_edit(current_user)

    db_link = RidgeInfoLink(
        ridge_id=ridge.id,
        link=infolink.link,
        description=infolink.description,
    )

    session.add(db_link)
    session.commit()
    session.refresh(db_link)
    return db_link


@router.delete("/ridge/{slug}")
async def delete_ridge(
    slug: str,
    current_user: Annotated[APIUser, Depends(get_current_active_user)],
    session: Session = Depends(get_session),
) -> ResponceStatus:
    """delete the ridge"""
    ridge = checked_ridge(session, slug=slug)

    can_edit(current_user)

    session.delete(ridge)
    session.commit()

    return ResponceStatus(
        status=True, message=_("Ridge {} deleted succesfully").format(slug)
    )


@router.delete("/ridge/link/{link_id}")
async def delete_ridge_link(
    link_id: int,
    current_user: Annotated[APIUser, Depends(get_current_active_user)],
    session: Session = Depends(get_session),
) -> ResponceStatus:
    """delete the ridge link"""
    statement = select(RidgeInfoLink).where(RidgeInfoLink.id == link_id)
    link = session.exec(statement).first()
    if link is None:
        raise HTTPException(status_code=404, detail=_("Ridge info link not found"))
    can_edit(current_user)

    session.delete(link)
    session.commit()

    return ResponceStatus(
        status=True,
        message=_("Ridge link with id={} deleted succesfully").format(link_id),
    )


@router.get("/ridge/peaks/{slug}", response_model=list[PeakShortOut])
async def get_ridge_peaks(
    slug: str, session: Session = Depends(get_session)
) -> list[PeakShortOut]:
    """get list of ridge peaks"""
    ridge = checked_ridge(session, slug=slug)

    statement = select(Peak).where(Peak.ridge == ridge)
    peaks = session.exec(statement).all()
    peaks = [PeakShortOut.model_validate(peak) for peak in peaks]

    return peaks


@router.get("/peaks")
async def get_peaks(session: Session = Depends(get_session)) -> list[Peak]:
    """get list of all peaks"""
    peaks = session.exec(select(Peak)).all()
    return peaks


@router.get("/peaks/search", response_model=list[PeakOut])
async def search_peak(
    key: Annotated[str | None, Query(max_length=50)] = None,
    session: Session = Depends(get_session),
) -> list[PeakOut]:
    """search peaks by slug or name"""
    statement = select(Peak)
    if key:
        statement = statement.where(Peak.slug.contains(key) | Peak.name.contains(key))
    peaks = session.exec(statement).all()

    return peaks


@router.get("/peak/{slug}", response_model=PeakOut)
async def get_peak(slug: str, session: Session = Depends(get_session)) -> PeakOut:
    """get the peak by slug"""
    statement = select(Peak).where(Peak.slug == slug)
    peak = session.exec(statement).first()
    if peak is None:
        raise HTTPException(status_code=404, detail=_("Peak not found"))

    return peak


@router.post("/peaks/add", response_model=Peak)
async def add_peak(
    peak: PeakCreate,
    current_user: Annotated[APIUser, Depends(get_current_active_user)],
    session: Session = Depends(get_session),
) -> Peak:
    """add new peak"""
    can_add(current_user)

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
        slug=unique_slugify(Peak, peak.name),
        ridge_id=peak.ridge_id,
        height=peak.height,
        point_id=point_id,
        editor_id=current_user.id,
    )

    session.add(db_peak)
    session.commit()
    session.refresh(db_peak)
    return db_peak


@router.post("/peak/{peak_id}/add/photo", response_model=PeakPhoto)
async def add_peak_photo(
    peak_id: int,
    file: UploadFile,
    description: str | None,
    current_user: Annotated[APIUser, Depends(get_current_active_user)],
    session: Session = Depends(get_session),
) -> PeakPhoto:
    """add new peak photo"""
    checked_peak(session, peak_id=peak_id)

    can_edit(current_user)

    image_dir = Peak.path_to_images()
    try:
        file_path = f"{image_dir}/{file.filename}"
        with open(file_path, "wb") as _file:
            _file.write(file.file.read())
            # return {'message': 'File saved successfully', 'success': True}
        _path = Peak.db_path_to_images()
        photo_path = f"{_path}/{file.filename}"
        image = PeakPhoto(peak_id=peak_id, photo=photo_path, description=description)

        session.add(image)
        session.commit()
        session.refresh(image)

        return image

    except Exception as error:
        return {"message": error.args, "success": False}


@router.put("/peak/{slug}", response_model=Peak)
async def update_peak(
    slug: str,
    peak: PeakCreate,
    current_user: Annotated[APIUser, Depends(get_current_active_user)],
    session: Session = Depends(get_session),
) -> Peak:
    """update the peak fields"""
    db_peak = checked_peak(session, slug=slug)

    can_edit(current_user)

    peak_dict = peak.model_dump(exclude_unset=True)
    for key, value in peak_dict.items():
        if key == "point_id":
            continue
        setattr(db_peak, key, value)

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
    peak_id: int,
    file: UploadFile,
    current_user: Annotated[APIUser, Depends(get_current_active_user)],
    session: Session = Depends(get_session),
) -> Peak:
    """update the peak photo"""
    peak = checked_peak(session, peak_id=peak_id)

    can_edit(current_user)

    image_dir = Peak.path_to_images()
    try:
        file_path = f"{image_dir}/{file.filename}"
        with open(file_path, "wb") as _file:
            _file.write(file.file.read())

        _path = Peak.db_path_to_images()
        photo_path = f"{_path}/{file.filename}"
        peak.photo = photo_path

        session.add(peak)
        session.commit()
        session.refresh(peak)

        return peak

    except Exception as error:
        return {"message": error.args, "success": False}


@router.delete("/peak/{slug}")
async def delete_peak(
    slug: str,
    current_user: Annotated[APIUser, Depends(get_current_active_user)],
    session: Session = Depends(get_session),
) -> ResponceStatus:
    """delete the peak"""
    peak = checked_peak(session, slug=slug)

    can_edit(current_user, peak)

    session.delete(peak)
    session.commit()

    return ResponceStatus(
        status=True, message=_("Peak {} deleted succesfully").format(slug)
    )


@router.delete("/peak/photo/{photo_id}")
async def delete_peak_photo(
    photo_id: int,
    current_user: Annotated[APIUser, Depends(get_current_active_user)],
    session: Session = Depends(get_session),
) -> ResponceStatus:
    """delete the peak photo"""
    statement = select(PeakPhoto).where(PeakPhoto.id == photo_id)
    photo = session.exec(statement).first()
    if photo is None:
        raise HTTPException(status_code=404, detail=_("Peak photo not found"))
    can_edit(current_user, photo.peak)

    session.delete(photo)
    session.commit()

    return ResponceStatus(
        status=True,
        message=_("Peak photo with id={} deleted succesfully").format(photo_id),
    )


@router.get("/peak/routes/{slug}", response_model=list[RouteListItem])
async def get_peak_routes(
    slug: str, session: Session = Depends(get_session)
) -> list[RouteListItem]:
    """get list of peak routes"""
    peak = checked_peak(session, slug=slug)

    statement = select(Route).where(Route.peak == peak)
    routers = session.exec(statement).all()
    return routers


@router.get("/routes")
async def get_routes(session: Session = Depends(get_session)) -> list[Route]:
    """get list of all routes"""
    routes = session.exec(select(Route)).all()
    return routes


@router.get("/routes/search", response_model=list[RouteListItem])
async def search_route(
    query: Annotated[str | None, Query(max_length=50)] = None,
    author: Annotated[str | None, Query(max_length=50)] = None,
    category: Annotated[str | None, Query(max_length=50)] = None,
    session: Session = Depends(get_session),
) -> list[RouteListItem]:
    """search routes by slug or name"""
    statement = select(Route)
    if query:
        statement = statement.where(
            Route.slug.contains(query) | Route.name.contains(query)
        )
    if author:
        statement = statement.where(Route.author.contains(author))
    if category:
        statement = statement.where(Route.difficulty.startswith(category))
    routes = session.exec(statement).all()

    return routes


@router.get("/route/{slug}")
async def get_route(slug: str, session: Session = Depends(get_session)) -> RouteOut:
    """get the route by slug"""
    route = checked_route(session, slug=slug)

    route_out = RouteOut.model_validate(route)

    return route_out


@router.post("/routes/add", response_model=Route)
async def add_route(
    route: RouteCreate,
    current_user: Annotated[APIUser, Depends(get_current_active_user)],
    session: Session = Depends(get_session),
) -> Route:
    """add new route"""
    can_add(current_user)

    db_route = Route(
        name=route.name,
        description=route.description,
        short_description=route.short_description,
        recommended_equipment=route.recommended_equipment,
        slug=unique_slugify(Route, route.name),
        peak_id=route.peak_id,
        difficulty=route.difficulty,
        max_difficulty=route.max_difficulty,
        author=route.author,
        length=route.length,
        year=route.year,
        height_difference=route.height_difference,
        start_height=route.start_height,
        descent=route.descent,
        editor_id=current_user.id,
    )

    session.add(db_route)
    session.commit()
    session.refresh(db_route)
    return db_route


@router.post("/route/{route_id}/add/section", response_model=RouteSection)
async def add_route_section(
    route_id: int,
    section: RouteSectionCreate,
    current_user: Annotated[APIUser, Depends(get_current_active_user)],
    session: Session = Depends(get_session),
) -> RouteSection:
    """add new route section"""
    route = checked_route(session, route_id=route_id)

    can_edit(current_user, route)

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


@router.post("/route/{route_id}/add/point", response_model=RoutePoint)
async def add_route_point(
    route_id: int,
    point: RoutePointCreate,
    current_user: Annotated[APIUser, Depends(get_current_active_user)],
    session: Session = Depends(get_session),
) -> RoutePoint:
    """add new route point"""
    route = checked_route(session, route_id=route_id)

    can_edit(current_user, route)

    point_id = None
    if point.point:
        _db_point = GeoPoint(
            latitude=point.point.latitude,
            longitude=point.point.longitude,
        )
        session.add(_db_point)
        session.commit()
        session.refresh(_db_point)
        point_id = _db_point.id

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
    route_id: int,
    file: UploadFile,
    description: str | None,
    current_user: Annotated[APIUser, Depends(get_current_active_user)],
    session: Session = Depends(get_session),
) -> RoutePhoto:
    """add new route photo"""
    route = checked_route(session, route_id=route_id)

    can_edit(current_user, route)

    image_dir = Route.path_to_images()
    try:
        file_path = f"{image_dir}/{file.filename}"
        with open(file_path, "wb") as _file:
            _file.write(file.file.read())

        _path = Route.db_path_to_images()
        photo_path = f"{_path}/{file.filename}"
        image = RoutePhoto(route_id=route_id, photo=photo_path, description=description)

        session.add(image)
        session.commit()
        session.refresh(image)

        return image

    except Exception as error:
        return {"message": error.args, "success": False}


@router.put("/route/{route_id}/map", response_model=Route)
async def update_route_map(
    route_id: int,
    file: UploadFile,
    current_user: Annotated[APIUser, Depends(get_current_active_user)],
    session: Session = Depends(get_session),
) -> Route:
    """update route map"""
    route = checked_route(session, route_id=route_id)

    can_edit(current_user, route)

    image_dir = Route.path_to_images()
    try:
        file_path = f"{image_dir}/{file.filename}"
        with open(file_path, "wb") as _file:
            _file.write(file.file.read())

        _path = Route.db_path_to_images()
        photo_path = f"{_path}/{file.filename}"
        route.map_image = photo_path

        session.add(route)
        session.commit()
        session.refresh(route)

        return route

    except Exception as error:
        return {"message": error.args, "success": False}


@router.put("/route/{route_id}/photo", response_model=Route)
async def update_route_photo(
    route_id: int,
    file: UploadFile,
    current_user: Annotated[APIUser, Depends(get_current_active_user)],
    session: Session = Depends(get_session),
) -> Peak:
    """update route photo"""
    route = checked_route(session, route_id=route_id)

    can_edit(current_user, route)

    image_dir = Route.path_to_images()
    try:
        file_path = f"{image_dir}/{file.filename}"
        with open(file_path, "wb") as _file:
            _file.write(file.file.read())

        _path = Route.db_path_to_images()
        photo_path = f"{_path}/{file.filename}"
        route.photo = photo_path

        session.add(route)
        session.commit()
        session.refresh(route)

        return route

    except Exception as error:
        return {"message": error.args, "success": False}


@router.put("/route/{route_id}", response_model=Route)
async def update_route(
    route_id: int,
    route: RouteCreate,
    current_user: Annotated[APIUser, Depends(get_current_active_user)],
    session: Session = Depends(get_session),
) -> Route:
    """update route fields"""
    db_route = checked_route(session, route_id=route_id)

    can_edit(current_user, route)

    route_dict = route.model_dump(exclude_unset=True)
    for key, value in route_dict.items():
        setattr(db_route, key, value)

    session.add(db_route)
    session.commit()
    session.refresh(db_route)

    return db_route


@router.put("/route/section/{section_id}", response_model=RouteSection)
async def update_route_section(
    section_id: int,
    section: RouteSectionCreate,
    current_user: Annotated[APIUser, Depends(get_current_active_user)],
    session: Session = Depends(get_session),
) -> RouteSection:
    """update route section"""
    statement = select(RouteSection).where(RouteSection.id == section_id)
    db_section = session.exec(statement).first()
    if not db_section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=_("Route section not found")
        )
    can_edit(current_user, db_section.route)

    section_dict = section.model_dump(exclude_unset=True)
    for key, value in section_dict.items():
        setattr(db_section, key, value)

    session.add(db_section)
    session.commit()
    session.refresh(db_section)

    return db_section


@router.delete("/route/{slug}")
async def delete_route(
    slug: str,
    current_user: Annotated[APIUser, Depends(get_current_active_user)],
    session: Session = Depends(get_session),
) -> ResponceStatus:
    """delete the route"""
    route = checked_route(session, slug=slug)

    can_edit(current_user, route)

    session.delete(route)
    session.commit()

    return ResponceStatus(
        status=True, message=_("Route {} deleted succesfully").format(slug)
    )


@router.delete("/route/point/{point_id}")
async def delete_route_point(
    point_id: int,
    current_user: Annotated[APIUser, Depends(get_current_active_user)],
    session: Session = Depends(get_session),
) -> ResponceStatus:
    """delete route point"""
    statement = select(RoutePoint).where(RoutePoint.id == point_id)
    point = session.exec(statement).first()
    if point is None:
        raise HTTPException(status_code=404, detail=_("Route point not found"))
    can_edit(current_user, point.route)

    session.delete(point)
    session.commit()

    return ResponceStatus(
        status=True,
        message=_("Route point with id={} deleted succesfully").format(point_id),
    )


@router.delete("/route/section/{section_id}")
async def delete_route_section(
    section_id: int,
    current_user: Annotated[APIUser, Depends(get_current_active_user)],
    session: Session = Depends(get_session),
) -> ResponceStatus:
    """delete route section"""
    statement = select(RouteSection).where(RouteSection.id == section_id)
    section = session.exec(statement).first()
    if section is None:
        raise HTTPException(status_code=404, detail=_("Route section not found"))
    can_edit(current_user, section.route)

    session.delete(section)
    session.commit()

    return ResponceStatus(
        status=True,
        message=_("Route section with id={} deleted succesfully").format(section_id),
    )
