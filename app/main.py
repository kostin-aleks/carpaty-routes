"""
MAIN
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqladmin import Admin

from .dependencies import db
from .models.admin import APIUserAdmin, PeakAdmin, RidgeAdmin, RouteAdmin
from .routers import mountains, users

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/media", StaticFiles(directory="data"), name="media")

app.include_router(mountains.router)
app.include_router(users.router)

admin = Admin(app, db)
admin.add_view(APIUserAdmin)
admin.add_view(RidgeAdmin)
admin.add_view(PeakAdmin)
admin.add_view(RouteAdmin)


@app.get("/")
async def root():
    """
    fake end-point
    """
    return {"application": "Carpathians winter routes"}
