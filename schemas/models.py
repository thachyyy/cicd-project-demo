from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


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


class UserCreate(BaseModel):
    email: EmailStr
    name: str = Field(min_length=1)
    password: str = Field(min_length=8, max_length=128)


class UserUpdate(BaseModel):
    """Only the fields that are sent get changed."""

    email: Optional[EmailStr] = None
    name: Optional[str] = Field(default=None, min_length=1)
    password: Optional[str] = Field(default=None, min_length=8, max_length=128)


class User(BaseModel):
    """What the API returns. It never includes the password or its hash."""

    id: UUID
    email: EmailStr
    name: str

    model_config = ConfigDict(from_attributes=True)


class UserDeleted(BaseModel):
    detail: str
