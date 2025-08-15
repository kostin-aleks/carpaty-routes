"""
Manage commands
"""

import inspect
import sys

import pwinput
import typer
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlmodel import select

from dependencies import config, get_password_hash, get_session
from models.users import APIUser

app = typer.Typer()


@app.command()
def hello(txt: str):
    """test command"""
    print(f"HELLO {txt}")


@app.command()
def commands():
    """list of commands"""
    _imported = ("get_password_hash", "get_session")
    _list = [
        f[0].replace("_", "-")
        for f in inspect.getmembers(sys.modules["__main__"], inspect.isfunction)
        if f[0] not in _imported
    ]
    for item in _list:
        print(item)


@app.command()
def create_admin(name: str, password: str, email: str):
    """create new user with admin permission"""
    db: Session = next(get_session())

    user = APIUser()
    user.username = name
    user.password = get_password_hash(password)
    user.email = email
    user.is_active = True
    user.is_admin = True

    db.add(user)
    db.commit()
    db.refresh(user)

    print(f"Created admin user {name}")


@app.command()
def change_password(username: str):
    """change user's password"""
    db: Session = next(get_session())

    statement = select(APIUser).where(APIUser.username == username)
    user = db.exec(statement).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Username not found",
        )
    password = pwinput.pwinput(prompt="Password: ", mask="*")
    user.password = get_password_hash(password)

    db.add(user)
    db.commit()
    db.refresh(user)

    print("Changed user's password")


@app.command()
def add_test_user():
    """add test user"""
    db: Session = next(get_session())

    statement = select(APIUser).where(
        APIUser.username == config("TEST_USERNAME", cast=str)
    )
    user = db.exec(statement).first()

    if not user:
        hashed_password = get_password_hash(config("TEST_PASSWORD", cast=str))
        user = APIUser(
            username=config("TEST_USERNAME", cast=str),
            email=config("TEST_EMAIL", cast=str),
            password=hashed_password,
            first_name="Ivan",
            last_name="Ivanov",
        )

        db.add(user)
        db.commit()
        db.refresh(user)

    print(f"Test user {user.username} is ready to test")


if __name__ == "__main__":

    app()
