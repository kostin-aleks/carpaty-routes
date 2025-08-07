from typing import Union

from fastapi import FastAPI, Depends
from fastadmin import fastapi_app as admin_app

from .routers import mountains
from .routers import users

app = FastAPI()

app.include_router(mountains.router)
app.include_router(users.router)

app.mount("/admin", admin_app)


@app.get("/")
async def root():
    return {"application": "Carpathians winter routes"}
