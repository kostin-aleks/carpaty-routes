"""
tests for router User
"""
import json

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.database import db
from app.main import app
from app.models.users import APIUser
from app.routers.users import verify_password
from app.settings import config

client = TestClient(app)


@pytest.fixture
def the_user():
    """fixture the_user"""
    session = Session(db)
    statement = select(APIUser).where(
        APIUser.username == config("TEST_USERNAME", cast=str)
    )
    user = session.exec(statement).first()
    return user


@pytest.fixture
def the_token():
    """fixture the_token"""
    form_data = {
        "username": config("TEST_USERNAME", cast=str),
        "password": config("TEST_PASSWORD", cast=str),
    }
    response = client.post("/users/token", data=form_data)
    assert response.status_code == 200
    data = json.loads(response.content)

    return data


def test_read_me(the_token):
    """test read me"""
    response = client.get(
        "/users/me", headers={"Authorization": f"Bearer {the_token['access_token']}"}
    )
    assert response.status_code == 200
    data = response.json()

    assert data["username"]
    assert data["email"]
    assert data["is_admin"]


def test_put_user(the_user, the_token):
    """test put user"""
    _buffer = the_user.middle_name
    _test = "Middle"
    post_data = {
        "username": the_user.username,
        "middle_name": _test,
    }
    response = client.put(
        f"/users/update/{the_user.id}",
        json=post_data,
        headers={"Authorization": f"Bearer {the_token['access_token']}"},
    )
    assert response.status_code == 200
    data = response.json()

    assert data["middle_name"] == _test
    assert data["username"] == the_user.username

    post_data = {
        "username": the_user.username,
        "middle_name": _buffer,
    }
    response = client.put(
        f"/users/update/{the_user.id}",
        json=post_data,
        headers={"Authorization": f"Bearer {the_token['access_token']}"},
    )
    assert response.status_code == 200
    data = response.json()

    assert data["middle_name"] == ""
    assert data["username"] == the_user.username


def test_set_user_permission(the_user, the_token):
    """test set user permission"""
    _buffer = the_user.is_editor
    post_data = {
        "is_editor": True,
    }
    response = client.put(
        f"/users/set/permissions/{the_user.id}",
        json=post_data,
        headers={"Authorization": f"Bearer {the_token['access_token']}"},
    )
    assert response.status_code == 200
    data = response.json()

    assert data["is_editor"]

    post_data = {
        "is_editor": _buffer,
    }
    response = client.put(
        f"/users/set/permissions/{the_user.id}",
        json=post_data,
        headers={"Authorization": f"Bearer {the_token['access_token']}"},
    )
    assert response.status_code == 200
    data = response.json()

    assert data["is_editor"] == _buffer


def test_update_email(the_user, the_token):
    """test update email"""
    _buffer = the_user.email
    _test = "test@email.com"
    post_data = {
        "username": the_user.username,
        "email": the_user.email,
        "new_email": _test,
    }
    response = client.put(
        "/users/email/update",
        json=post_data,
        headers={"Authorization": f"Bearer {the_token['access_token']}"},
    )
    assert response.status_code == 200
    data = response.json()

    assert data["email"] == _test

    post_data = {
        "username": the_user.username,
        "email": _test,
        "new_email": _buffer,
    }
    response = client.put(
        "/users/email/update",
        json=post_data,
        headers={"Authorization": f"Bearer {the_token['access_token']}"},
    )
    assert response.status_code == 200
    data = response.json()

    assert data["email"] == _buffer


def test_update_password(the_user, the_token):
    """test update password"""
    _buffer = config("TEST_PASSWORD", cast=str)
    _test = "kjnbetuivcstrll34ccgh"
    post_data = {
        "username": the_user.username,
        "password": _buffer,
        "new_password": _test,
    }
    response = client.put(
        "/users/password/update",
        json=post_data,
        headers={"Authorization": f"Bearer {the_token['access_token']}"},
    )
    assert response.status_code == 200
    data = response.json()

    assert verify_password(_test, data["password"])

    post_data = {
        "username": the_user.username,
        "password": _test,
        "new_password": _buffer,
    }
    response = client.put(
        "/users/password/update",
        json=post_data,
        headers={"Authorization": f"Bearer {the_token['access_token']}"},
    )
    assert response.status_code == 200
    data = response.json()

    assert verify_password(_buffer, data["password"])
