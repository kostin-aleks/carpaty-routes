from sqladmin import ModelView

from app.models.mountains import Peak, Ridge, Route
from app.models.users import APIUser


class APIUserAdmin(ModelView, model=APIUser):
    column_list = [
        APIUser.id,
        APIUser.username,
        APIUser.email,
        APIUser.first_name,
        APIUser.last_name,
        APIUser.is_admin,
        APIUser.is_editor,
        APIUser.is_active,
        APIUser.date_joined,
    ]


class RidgeAdmin(ModelView, model=Ridge):
    column_list = [
        Ridge.id,
        Ridge.slug,
        Ridge.name,
        Ridge.description,
        Ridge.editor_id,
        Ridge.active,
        Ridge.changed,
    ]

    column_details_list = [
        Ridge.id,
        Ridge.slug,
        Ridge.name,
        Ridge.description,
        Ridge.editor_id,
        Ridge.active,
        Ridge.changed,
    ]


class PeakAdmin(ModelView, model=Peak):
    column_list = [
        Peak.id,
        Peak.slug,
        Peak.name,
        Peak.ridge_id,
        Peak.active,
        Peak.changed,
    ]

    column_details_list = [
        Peak.id,
        Peak.slug,
        Peak.name,
        Peak.ridge_id,
        Peak.height,
        Peak.point,
        Peak.photo,
        Peak.editor_id,
        Peak.active,
        Peak.changed,
    ]


class RouteAdmin(ModelView, model=Route):
    column_list = [
        Route.id,
        Route.peak_id,
        Route.name,
        Route.slug,
        Route.ready,
    ]
    column_details_list = [
        Route.id,
        Route.peak_id,
        Route.name,
        Route.slug,
        Route.description,
        Route.short_description,
        Route.recommended_equipment,
        Route.photo,
        Route.map_image,
        Route.difficulty,
        Route.max_difficulty,
        Route.author,
        Route.length,
        Route.year,
        Route.height_difference,
        Route.start_height,
        Route.descent,
        Route.editor_id,
        Route.ready,
        Route.changed,
    ]
