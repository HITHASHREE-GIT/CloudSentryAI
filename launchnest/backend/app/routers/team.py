"""
LaunchNest — Team Router
=========================
List all users (team members).
"""

from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.security import get_current_user

router = APIRouter(prefix="/api/team", tags=["Team"])


@router.get("", response_model=List[schemas.UserOut])
def list_team(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return db.query(models.User).order_by(models.User.user_id).all()