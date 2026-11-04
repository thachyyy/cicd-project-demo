from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.connection import get_db
from schemas.models import Article, ArticleDeleted, ArticleUpdate
from utils import article_crud

router = APIRouter(tags=["articles"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=Article)
def add_article(article: Article, db: Session = Depends(get_db)):
    return article_crud.create_article(db=db, article=article)


@router.get("", response_model=List[Article])
def read_articles(db: Session = Depends(get_db)):
    return article_crud.list_articles(db=db)


@router.get("/{article_id}", response_model=Article)
def read_article(article_id: UUID, db: Session = Depends(get_db)):
    return article_crud.get_article(db=db, article_id=article_id)


@router.patch("/{article_id}", response_model=Article)
def edit_article(
    article_id: UUID, changes: ArticleUpdate, db: Session = Depends(get_db)
):
    return article_crud.update_article(db=db, article_id=article_id, changes=changes)


@router.delete("/{article_id}", response_model=ArticleDeleted)
def remove_article(article_id: UUID, db: Session = Depends(get_db)):
    result = article_crud.delete_article(db=db, article_id=article_id)
    if result.detail == article_crud.ARTICLE_MISSING:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Article not found"
        )
    return result
