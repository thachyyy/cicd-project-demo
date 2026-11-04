from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.connection import get_db
from schemas.models import User, UserCreate, UserDeleted, UserUpdate
from utils import user_crud

router = APIRouter(tags=["users"])

EMAIL_TAKEN = HTTPException(
    status_code=status.HTTP_409_CONFLICT, detail="Email is already in use"
)
USER_NOT_FOUND = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
)


@router.post("", status_code=status.HTTP_201_CREATED, response_model=User)
def add_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        return user_crud.create_user(db=db, user=user)
    except user_crud.EmailTaken:
        raise EMAIL_TAKEN


@router.get("", response_model=List[User])
def read_users(db: Session = Depends(get_db)):
    return user_crud.list_users(db=db)


@router.get("/{user_id}", response_model=User)
def read_user(user_id: UUID, db: Session = Depends(get_db)):
    user = user_crud.get_user(db=db, user_id=user_id)
    if user is None:
        raise USER_NOT_FOUND
    return user


@router.patch("/{user_id}", response_model=User)
def edit_user(user_id: UUID, changes: UserUpdate, db: Session = Depends(get_db)):
    try:
        user = user_crud.update_user(db=db, user_id=user_id, changes=changes)
    except user_crud.EmailTaken:
        raise EMAIL_TAKEN
    if user is None:
        raise USER_NOT_FOUND
    return user


@router.delete("/{user_id}", response_model=UserDeleted)
def remove_user(user_id: UUID, db: Session = Depends(get_db)):
    if not user_crud.delete_user(db=db, user_id=user_id):
        raise USER_NOT_FOUND
    return UserDeleted(detail="User deleted")
