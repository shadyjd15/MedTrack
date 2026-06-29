from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from .. import models, schemas, auth
from ..database import get_db

router = APIRouter(prefix="/api/caregivers", tags=["caregivers"])


@router.get("/links", response_model=List[schemas.CaregiverLinkOut])
def list_links(db: Session = Depends(get_db), admin: models.User = Depends(auth.require_admin)):
    """Admin-only: list every caregiver -> patient link in the system."""
    links = db.query(models.CaregiverLink).options(
        joinedload(models.CaregiverLink.caregiver), joinedload(models.CaregiverLink.patient)
    ).all()
    out = []
    for l in links:
        item = schemas.CaregiverLinkOut.model_validate(l)
        item.caregiver_name = l.caregiver.full_name or l.caregiver.username
        item.patient_name = l.patient.full_name or l.patient.username
        out.append(item)
    return out


@router.post("/links", response_model=schemas.CaregiverLinkOut)
def create_link(payload: schemas.CaregiverLinkCreate, db: Session = Depends(get_db), admin: models.User = Depends(auth.require_admin)):
    caregiver = db.query(models.User).filter(models.User.id == payload.caregiver_id).first()
    patient = db.query(models.User).filter(models.User.id == payload.patient_id).first()
    if not caregiver or caregiver.role != models.RoleEnum.caregiver:
        raise HTTPException(status_code=400, detail="caregiver_id must reference a user with the 'caregiver' role")
    if not patient:
        raise HTTPException(status_code=400, detail="patient_id not found")
    existing = db.query(models.CaregiverLink).filter(
        models.CaregiverLink.caregiver_id == payload.caregiver_id,
        models.CaregiverLink.patient_id == payload.patient_id,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="This link already exists")
    link = models.CaregiverLink(caregiver_id=payload.caregiver_id, patient_id=payload.patient_id)
    db.add(link)
    db.commit()
    db.refresh(link)
    out = schemas.CaregiverLinkOut.model_validate(link)
    out.caregiver_name = caregiver.full_name or caregiver.username
    out.patient_name = patient.full_name or patient.username
    return out


@router.delete("/links/{link_id}")
def delete_link(link_id: str, db: Session = Depends(get_db), admin: models.User = Depends(auth.require_admin)):
    link = db.query(models.CaregiverLink).filter(models.CaregiverLink.id == link_id).first()
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    db.delete(link)
    db.commit()
    return {"ok": True}


@router.get("/my-patients", response_model=List[schemas.UserOut])
def my_patients(db: Session = Depends(get_db), user: models.User = Depends(auth.get_current_user)):
    """Caregiver-only: list the patients this caregiver account is linked to."""
    if user.role != models.RoleEnum.caregiver:
        return []
    links = db.query(models.CaregiverLink).options(joinedload(models.CaregiverLink.patient)).filter(
        models.CaregiverLink.caregiver_id == user.id
    ).all()
    return [l.patient for l in links]
