"""Integration tests: requests go through the API to a real database.

Unlike test_articles.py, nothing is mocked here. GitHub Actions runs these
against PostgreSQL; locally they use SQLite unless DATABASE_URL is set.
"""

import os
from uuid import UUID, uuid4

from fastapi import status
from fastapi.testclient import TestClient
import pytest

os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")

from database.connection import SessionLocal
from database.models import User as UserRow
from main import app
from utils.passwords import verify_password

client = TestClient(app)

USER_PASSWORD = "correct horse battery"


@pytest.fixture
def article():
    """Create an article for a test, then remove it so no data is left behind."""
    response = client.post(
        "/articles",
        # uuid4 keeps the title unique, so tests never match each other's rows.
        json={"title": f"Title {uuid4()}", "description": "Saved in the database"},
    )
    assert response.status_code == status.HTTP_201_CREATED
    created = response.json()
    yield created
    client.delete(f"/articles/{created['id']}")


def test_created_article_can_be_read_back(article):
    response = client.get(f"/articles/{article['id']}")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == article


def test_created_article_appears_in_list(article):
    response = client.get("/articles")

    assert response.status_code == status.HTTP_200_OK
    assert article["id"] in [item["id"] for item in response.json()]


def test_edit_is_saved(article):
    changes = {"title": article["title"], "description": "Edited description"}

    edit_response = client.patch(f"/articles/{article['id']}", json=changes)
    read_response = client.get(f"/articles/{article['id']}")

    assert edit_response.status_code == status.HTTP_200_OK
    assert read_response.json()["description"] == "Edited description"


def test_delete_removes_article(article):
    delete_response = client.delete(f"/articles/{article['id']}")
    list_response = client.get("/articles")

    assert delete_response.status_code == status.HTTP_200_OK
    assert article["id"] not in [item["id"] for item in list_response.json()]


def test_deleting_missing_article_returns_404():
    response = client.delete(f"/articles/{uuid4()}")

    assert response.status_code == status.HTTP_404_NOT_FOUND


def unique_email():
    return f"{uuid4()}@example.com"


def stored_password_hash(user_id):
    with SessionLocal() as db:
        return db.query(UserRow).filter_by(id=UUID(user_id)).one().hashed_password


@pytest.fixture
def user():
    """Create a user for a test, then remove it so no data is left behind."""
    response = client.post(
        "/users",
        json={"email": unique_email(), "name": "Ada", "password": USER_PASSWORD},
    )
    assert response.status_code == status.HTTP_201_CREATED
    created = response.json()
    yield created
    client.delete(f"/users/{created['id']}")


def test_created_user_can_be_read_back(user):
    response = client.get(f"/users/{user['id']}")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == user


def test_created_user_appears_in_list(user):
    response = client.get("/users")

    assert response.status_code == status.HTTP_200_OK
    assert user["id"] in [item["id"] for item in response.json()]


def test_password_is_stored_hashed_and_never_returned(user):
    stored = stored_password_hash(user["id"])

    assert set(user) == {"id", "email", "name"}
    assert stored != USER_PASSWORD
    assert verify_password(USER_PASSWORD, stored)


def test_edit_changes_only_the_fields_sent(user):
    original_hash = stored_password_hash(user["id"])

    response = client.patch(f"/users/{user['id']}", json={"name": "Grace"})

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {**user, "name": "Grace"}
    assert stored_password_hash(user["id"]) == original_hash


def test_edit_can_change_password(user):
    new_password = "a different password"

    response = client.patch(f"/users/{user['id']}", json={"password": new_password})

    assert response.status_code == status.HTTP_200_OK
    assert verify_password(new_password, stored_password_hash(user["id"]))


def test_creating_user_with_taken_email_returns_409(user):
    response = client.post(
        "/users",
        json={"email": user["email"], "name": "Copy", "password": USER_PASSWORD},
    )

    assert response.status_code == status.HTTP_409_CONFLICT


def test_editing_user_to_taken_email_returns_409_and_keeps_data(user):
    other = client.post(
        "/users",
        json={"email": unique_email(), "name": "Other", "password": USER_PASSWORD},
    ).json()

    response = client.patch(f"/users/{other['id']}", json={"email": user["email"]})
    read_response = client.get(f"/users/{other['id']}")
    client.delete(f"/users/{other['id']}")

    assert response.status_code == status.HTTP_409_CONFLICT
    assert read_response.json() == other


def test_delete_removes_user(user):
    delete_response = client.delete(f"/users/{user['id']}")
    read_response = client.get(f"/users/{user['id']}")

    assert delete_response.status_code == status.HTTP_200_OK
    assert read_response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.parametrize(
    "method, body",
    [("get", None), ("patch", {"name": "Grace"}), ("delete", None)],
)
def test_missing_user_returns_404(method, body):
    response = client.request(method, f"/users/{uuid4()}", json=body)

    assert response.status_code == status.HTTP_404_NOT_FOUND
