"""
Manage commands
"""
import inspect
from pathlib import Path
import sys
import typer
from sqlalchemy.orm import Session

#from database import get_session
from dependencies import get_password_hash
from models.users import APIUser

app = typer.Typer()


@app.command()
def hello(txt: str):
    """test command"""
    print(f"HELLO {txt}")


@app.command()
def commands():
    """list of commands"""
    _imported = ('get_password_hash')
    _list = [
        f[0] for f
        in inspect.getmembers(sys.modules['__main__'], inspect.isfunction)
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


if __name__ == "__main__":

    app()
