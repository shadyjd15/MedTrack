from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas, auth
from ..database import get_db

router = APIRouter(prefix="/api/allergies", tags=["allergies"])


def _scope_query(db: Session, scope_user_id: Optional[str]):
    q = db.query(models.Allergy)
    if scope_user_id is not None:
        q = q.filter(models.Allergy.user_id == scope_user_id)
    return q


@router.get("", response_model=List[schemas.AllergyOut])
def list_allergies(
    db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user),
    scope_user_id: Optional[str] = Depends(auth.get_scope_user_id),
):
    return _scope_query(db, scope_user_id).order_by(models.Allergy.substance).all()


@router.post("", response_model=schemas.AllergyOut)
def create_allergy(
    payload: schemas.AllergyCreate, db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user),
    scope_user_id: Optional[str] = Depends(auth.get_scope_user_id),
):
    owner_id = scope_user_id if scope_user_id is not None else user.id
    a = models.Allergy(user_id=owner_id, **payload.model_dump())
    db.add(a)
    db.commit()
    db.refresh(a)
    return a


@router.put("/{allergy_id}", response_model=schemas.AllergyOut)
def update_allergy(
    allergy_id: str, payload: schemas.AllergyUpdate, db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user),
    scope_user_id: Optional[str] = Depends(auth.get_scope_user_id),
):
    a = _scope_query(db, scope_user_id).filter(models.Allergy.id == allergy_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Allergy record not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(a, k, v)
    db.commit()
    db.refresh(a)
    return a


@router.delete("/{allergy_id}")
def delete_allergy(
    allergy_id: str, db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user),
    scope_user_id: Optional[str] = Depends(auth.get_scope_user_id),
):
    a = _scope_query(db, scope_user_id).filter(models.Allergy.id == allergy_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Allergy record not found")
    db.delete(a)
    db.commit()
    return {"ok": True}
