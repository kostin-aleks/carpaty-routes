from sqladmin import Admin
from typing import Union

from fastapi import FastAPI, Depends

from .database import db
from .routers import mountains
from .routers import users
from .models.admin import APIUserAdmin, RidgeAdmin, PeakAdmin, RouteAdmin

app = FastAPI()

app.include_router(mountains.router)
app.include_router(users.router)

admin = Admin(app, db)
admin.add_view(APIUserAdmin)
admin.add_view(RidgeAdmin)
admin.add_view(PeakAdmin)
admin.add_view(RouteAdmin)


@app.get("/")
async def root():
    return {"application": "Carpathians winter routes"}
