from typing import Union

from fastapi import FastAPI, Depends
#from fastapi_amis_admin.admin.settings import Settings
#from fastapi_amis_admin.admin.site import AdminSite

#from .database import MYSQL_DATABASE_URL
from .adminsite import site
from .routers import mountains
from .routers import users

app = FastAPI()

app.include_router(mountains.router)
app.include_router(users.router)

#site = AdminSite(settings=Settings(database_url=MYSQL_DATABASE_URL))
site.mount_app(app)


@app.get("/")
async def root():
    return {"application": "Carpathians winter routes"}
