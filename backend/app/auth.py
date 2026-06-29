import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from . import models
from .database import get_db

SECRET_KEY = os.getenv("SECRET_KEY", "change-this-secret-key-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None or not user.is_active:
        raise credentials_exception
    return user


def require_admin(user: models.User = Depends(get_current_user)) -> models.User:
    if user.role != models.RoleEnum.admin:
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return user


def resolve_scope_user_id(current_user: models.User, x_patient_id: Optional[str], db: Session) -> Optional[str]:
    """
    Returns the user_id whose records the current request should operate on,
    or None to mean "no filtering" (admins see everyone's data, as before).

    - admin            -> None (sees / can act on everything)
    - caregiver         -> must pass a valid X-Patient-Id header for a linked patient
    - regular user      -> always scoped to themselves
    """
    if current_user.role == models.RoleEnum.admin:
        return None
    if current_user.role == models.RoleEnum.caregiver:
        if not x_patient_id:
            raise HTTPException(status_code=400, detail="Select a patient first (missing X-Patient-Id).")
        link = db.query(models.CaregiverLink).filter(
            models.CaregiverLink.caregiver_id == current_user.id,
            models.CaregiverLink.patient_id == x_patient_id,
        ).first()
        if not link:
            raise HTTPException(status_code=403, detail="You are not linked to this patient.")
        return x_patient_id
    return current_user.id


def get_scope_user_id(
    x_patient_id: Optional[str] = Header(default=None, alias="X-Patient-Id"),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Optional[str]:
    return resolve_scope_user_id(current_user, x_patient_id, db)
