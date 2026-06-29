from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas, auth, email_utils
from ..database import get_db

router = APIRouter(prefix="/api/users", tags=["users"])

VALID_ROLES = {"admin", "user", "caregiver"}


@router.get("", response_model=List[schemas.UserOut])
def list_users(db: Session = Depends(get_db), admin: models.User = Depends(auth.require_admin)):
    return db.query(models.User).order_by(models.User.created_at.desc()).all()


@router.post("", response_model=schemas.UserOut)
def create_user(payload: schemas.UserCreate, db: Session = Depends(get_db), admin: models.User = Depends(auth.require_admin)):
    existing = db.query(models.User).filter(models.User.username == payload.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    if payload.role not in VALID_ROLES:
        raise HTTPException(status_code=400, detail=f"role must be one of {sorted(VALID_ROLES)}")

    user = models.User(
        username=payload.username,
        hashed_password=auth.hash_password(payload.password),
        full_name=payload.full_name,
        email=payload.email,
        role=payload.role,
        currency=payload.currency or "USD",
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    if user.email:
        email_utils.notify_account_created(db, user.email, user.username, payload.password, user.full_name or "")

    return user


@router.put("/{user_id}", response_model=schemas.UserOut)
def update_user(user_id: str, payload: schemas.UserUpdate, db: Session = Depends(get_db), admin: models.User = Depends(auth.require_admin)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    data = payload.model_dump(exclude_unset=True)
    if "role" in data and data["role"] not in VALID_ROLES:
        raise HTTPException(status_code=400, detail=f"role must be one of {sorted(VALID_ROLES)}")

    password_changed = False
    if "password" in data and data["password"]:
        user.hashed_password = auth.hash_password(data.pop("password"))
        password_changed = True
    else:
        data.pop("password", None)

    for k, v in data.items():
        setattr(user, k, v)
    db.commit()
    db.refresh(user)

    if password_changed and user.email:
        email_utils.notify_password_changed(db, user.email, user.username)

    return user


@router.delete("/{user_id}")
def delete_user(user_id: str, db: Session = Depends(get_db), admin: models.User = Depends(auth.require_admin)):
    if user_id == admin.id:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"ok": True}


@router.put("/me/password")
def change_my_password(payload: dict, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    new_password = payload.get("password")
    if not new_password or len(new_password) < 4:
        raise HTTPException(status_code=400, detail="Password too short")
    current_user.hashed_password = auth.hash_password(new_password)
    db.commit()
    if current_user.email:
        email_utils.notify_password_changed(db, current_user.email, current_user.username)
    return {"ok": True}


@router.put("/me/theme", response_model=schemas.UserOut)
def update_my_theme(payload: dict, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    theme = payload.get("theme_preference")
    if theme not in ("light", "dark"):
        raise HTTPException(status_code=400, detail="theme_preference must be 'light' or 'dark'")
    current_user.theme_preference = theme
    db.commit()
    db.refresh(current_user)
    return current_user


@router.put("/me/currency", response_model=schemas.UserOut)
def update_my_currency(payload: dict, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    currency = payload.get("currency")
    if not currency or len(currency) > 8:
        raise HTTPException(status_code=400, detail="Invalid currency code")
    current_user.currency = currency.upper()
    db.commit()
    db.refresh(current_user)
    return current_user
