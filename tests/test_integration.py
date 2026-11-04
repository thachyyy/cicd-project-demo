"""Integration tests: requests go through the API to a real database.

Unlike test_articles.py, nothing is mocked here. GitHub Actions runs these
against PostgreSQL; locally they use SQLite unless DATABASE_URL is set.
"""

import os
from uuid import uuid4

from fastapi import status
from fastapi.testclient import TestClient
import pytest

os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")

from main import app

client = TestClient(app)


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
