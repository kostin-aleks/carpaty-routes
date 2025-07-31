from typing import Union

from fastapi import FastAPI, Depends
from .routers import mountains
# from .database import db

app = FastAPI()

app.include_router(mountains.router)


# @app.on_event("startup")
# async def startup():
#     await db.connect()
#
#
# @app.on_event("shutdown")
# async def shutdown():
#     await db.disconnect()


@app.get("/")
async def root():
    return {"Hello": "World"}

