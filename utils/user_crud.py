from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database.models import User as UserRow
from schemas.models import UserCreate, UserUpdate
from utils.passwords import hash_password


class EmailTaken(Exception):
    """Another account already uses this email address."""


def _commit(db: Session):
    # The unique constraint is the check, so two requests at once cannot both win.
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise EmailTaken from error


def create_user(db: Session, user: UserCreate):
    row = UserRow(
        email=user.email,
        name=user.name,
        hashed_password=hash_password(user.password),
    )
    db.add(row)
    _commit(db)
    db.refresh(row)
    return row


def list_users(db: Session):
    return db.query(UserRow).order_by(UserRow.id).all()


def get_user(db: Session, user_id: int):
    return db.query(UserRow).filter_by(id=user_id).first()


def update_user(db: Session, user_id: int, changes: UserUpdate):
    row = get_user(db=db, user_id=user_id)
    if row is None:
        return None

    if changes.email is not None:
        row.email = changes.email
    if changes.name is not None:
        row.name = changes.name
    if changes.password is not None:
        row.hashed_password = hash_password(changes.password)

    _commit(db)
    db.refresh(row)
    return row


def delete_user(db: Session, user_id: int) -> bool:
    row = get_user(db=db, user_id=user_id)
    if row is None:
        return False

    db.delete(row)
    db.commit()
    return True
