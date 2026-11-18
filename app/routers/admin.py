from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import admin_user
from app.models import User
from app.schemas import UserPublic

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/users", response_model=list[UserPublic])
def list_users(
    _admin: Annotated[User, Depends(admin_user)],
    db: Annotated[Session, Depends(get_db)],
):
    return db.scalars(select(User).order_by(User.id).limit(100)).all()
