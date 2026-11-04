import os
from unittest.mock import patch
from uuid import uuid4

from fastapi import status
from fastapi.testclient import TestClient
import pytest

os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")

from database.connection import get_db
from main import app
from schemas.models import Article, ArticleDeleted
from utils.article_crud import ARTICLE_REMOVED

client = TestClient(app)

ARTICLE_ID = uuid4()
SAMPLE_TITLE = "Release notes"
SAMPLE_DESCRIPTION = "What shipped this week"
EDITED_DESCRIPTION = "What shipped this month"


def sample_article(description=SAMPLE_DESCRIPTION):
    return Article(id=ARTICLE_ID, title=SAMPLE_TITLE, description=description)


@pytest.fixture(autouse=True)
def stub_database():
    def no_database():
        yield None

    app.dependency_overrides[get_db] = no_database
    yield
    app.dependency_overrides.clear()


def test_health_check():
    response = client.get("/")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "healthy"}


def test_create_article():
    with patch("utils.article_crud.create_article", return_value=sample_article()):
        response = client.post(
            "/articles",
            json={"title": SAMPLE_TITLE, "description": SAMPLE_DESCRIPTION},
        )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["title"] == SAMPLE_TITLE
    assert response.json()["description"] == SAMPLE_DESCRIPTION


def test_list_articles():
    with patch("utils.article_crud.list_articles", return_value=[sample_article()]):
        response = client.get("/articles")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1


def test_read_article():
    with patch("utils.article_crud.get_article", return_value=sample_article()):
        response = client.get(f"/articles/{ARTICLE_ID}")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == str(ARTICLE_ID)
    assert response.json()["title"] == SAMPLE_TITLE


def test_edit_article():
    with patch(
        "utils.article_crud.update_article",
        return_value=sample_article(EDITED_DESCRIPTION),
    ):
        response = client.patch(
            f"/articles/{ARTICLE_ID}",
            json={"title": SAMPLE_TITLE, "description": EDITED_DESCRIPTION},
        )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["description"] == EDITED_DESCRIPTION


def test_remove_article():
    with patch(
        "utils.article_crud.delete_article",
        return_value=ArticleDeleted(detail=ARTICLE_REMOVED),
    ):
        response = client.delete(f"/articles/{ARTICLE_ID}")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["detail"] == ARTICLE_REMOVED
