import os
from unittest.mock import patch

from fastapi import status
from fastapi.testclient import TestClient
import pytest

os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")

from database.connection import get_db
from main import app
from schemas.models import User
from utils.passwords import hash_password, verify_password
from utils.user_crud import EmailTaken

client = TestClient(app)

USER_ID = 1
SAMPLE_EMAIL = "ada@example.com"
SAMPLE_NAME = "Ada"
SAMPLE_PASSWORD = "correct horse battery"
NEW_USER = {"email": SAMPLE_EMAIL, "name": SAMPLE_NAME, "password": SAMPLE_PASSWORD}


def sample_user(name=SAMPLE_NAME):
    return User(id=USER_ID, email=SAMPLE_EMAIL, name=name)


@pytest.fixture(autouse=True)
def stub_database():
    def no_database():
        yield None

    app.dependency_overrides[get_db] = no_database
    yield
    app.dependency_overrides.clear()


def test_create_user():
    with patch("utils.user_crud.create_user", return_value=sample_user()):
        response = client.post("/users", json=NEW_USER)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {
        "id": USER_ID,
        "email": SAMPLE_EMAIL,
        "name": SAMPLE_NAME,
    }


def test_create_user_with_taken_email_returns_409():
    with patch("utils.user_crud.create_user", side_effect=EmailTaken):
        response = client.post("/users", json=NEW_USER)

    assert response.status_code == status.HTTP_409_CONFLICT


@pytest.mark.parametrize(
    "field, value",
    [("email", "not-an-email"), ("name", ""), ("password", "short")],
)
def test_create_user_rejects_invalid_input(field, value):
    response = client.post("/users", json={**NEW_USER, field: value})

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_list_users():
    with patch("utils.user_crud.list_users", return_value=[sample_user()]):
        response = client.get("/users")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1


def test_read_user():
    with patch("utils.user_crud.get_user", return_value=sample_user()):
        response = client.get(f"/users/{USER_ID}")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == USER_ID


def test_read_missing_user_returns_404():
    with patch("utils.user_crud.get_user", return_value=None):
        response = client.get(f"/users/{USER_ID}")

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_edit_user():
    with patch("utils.user_crud.update_user", return_value=sample_user("Grace")):
        response = client.patch(f"/users/{USER_ID}", json={"name": "Grace"})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name"] == "Grace"


def test_edit_missing_user_returns_404():
    with patch("utils.user_crud.update_user", return_value=None):
        response = client.patch(f"/users/{USER_ID}", json={"name": "Grace"})

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_edit_user_with_taken_email_returns_409():
    with patch("utils.user_crud.update_user", side_effect=EmailTaken):
        response = client.patch(f"/users/{USER_ID}", json={"email": SAMPLE_EMAIL})

    assert response.status_code == status.HTTP_409_CONFLICT


def test_remove_user():
    with patch("utils.user_crud.delete_user", return_value=True):
        response = client.delete(f"/users/{USER_ID}")

    assert response.status_code == status.HTTP_200_OK


def test_remove_missing_user_returns_404():
    with patch("utils.user_crud.delete_user", return_value=False):
        response = client.delete(f"/users/{USER_ID}")

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_password_hash_verifies_only_the_right_password():
    stored = hash_password(SAMPLE_PASSWORD)

    assert SAMPLE_PASSWORD not in stored
    assert verify_password(SAMPLE_PASSWORD, stored)
    assert not verify_password("wrong password", stored)


def test_same_password_hashes_differently_each_time():
    assert hash_password(SAMPLE_PASSWORD) != hash_password(SAMPLE_PASSWORD)
