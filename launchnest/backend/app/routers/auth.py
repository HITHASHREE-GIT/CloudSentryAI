"""
LaunchNest — Authentication Router
===================================
Endpoints: /register, /login, /me
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.security import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
)

router = APIRouter(prefix="/api/auth", tags=["Auth"])


# ═══════════════════════════════════════════════════════
# REGISTER
# ═══════════════════════════════════════════════════════

@router.post("/register", response_model=schemas.Token, status_code=201)
def register(payload: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if email exists
    existing = db.query(models.User).filter(models.User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create user
    user = models.User(
        name=payload.name,
        email=payload.email,
        password_hash=hash_password(payload.password),
        role=payload.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Log activity
    activity = models.Activity(user_id=user.user_id, action=f"registered as {user.role}")
    db.add(activity)
    db.commit()

    # Create token
    token = create_access_token({"sub": str(user.user_id)})
    return schemas.Token(access_token=token, user=schemas.UserOut.model_validate(user))


# ═══════════════════════════════════════════════════════
# LOGIN
# ═══════════════════════════════════════════════════════

@router.post("/login", response_model=schemas.Token)
def login(payload: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token({"sub": str(user.user_id)})
    return schemas.Token(access_token=token, user=schemas.UserOut.model_validate(user))


# ═══════════════════════════════════════════════════════
# ME (current user)
# ═══════════════════════════════════════════════════════

@router.get("/me", response_model=schemas.UserOut)
def me(current_user: models.User = Depends(get_current_user)):
    return current_user