from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class HealthStatus(BaseModel):
    status: str


class ArticleUpdate(BaseModel):
    title: str
    description: str


class Article(ArticleUpdate):
    id: Optional[UUID] = None

    model_config = ConfigDict(from_attributes=True)


class ArticleDeleted(BaseModel):
    detail: str
