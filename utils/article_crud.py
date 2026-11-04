from uuid import UUID

from sqlalchemy import delete, update
from sqlalchemy.orm import Session

from database.models import Article as ArticleRow
from schemas.models import Article, ArticleDeleted, ArticleUpdate

ARTICLE_MISSING = "Article does not exist"
ARTICLE_REMOVED = "Article deleted"


def create_article(db: Session, article: Article):
    row = ArticleRow(title=article.title, description=article.description)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def list_articles(db: Session):
    return db.query(ArticleRow).all()


def get_article(db: Session, article_id: UUID):
    return db.query(ArticleRow).filter_by(id=article_id).one()


def update_article(db: Session, article_id: UUID, changes: ArticleUpdate):
    db.execute(
        update(ArticleRow)
        .where(ArticleRow.id == article_id)
        .values(title=changes.title, description=changes.description)
    )
    db.commit()
    return get_article(db=db, article_id=article_id)


def delete_article(db: Session, article_id: UUID):
    if not db.query(ArticleRow).filter_by(id=article_id).first():
        return ArticleDeleted(detail=ARTICLE_MISSING)
    db.execute(delete(ArticleRow).where(ArticleRow.id == article_id))
    db.commit()
    return ArticleDeleted(detail=ARTICLE_REMOVED)
