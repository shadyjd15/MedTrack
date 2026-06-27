import os
import shutil
import uuid
from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from .. import models, schemas, auth
from ..database import get_db

router = APIRouter(prefix="/api/prescriptions", tags=["prescriptions"])

UPLOAD_DIR = "uploads/prescriptions"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def _scope_query(db: Session, user: models.User):
    q = db.query(models.Prescription)
    if user.role != models.RoleEnum.admin:
        q = q.filter(models.Prescription.user_id == user.id)
    return q


@router.get("", response_model=List[schemas.PrescriptionOut])
def list_prescriptions(db: Session = Depends(get_db), user: models.User = Depends(auth.get_current_user)):
    return _scope_query(db, user).order_by(models.Prescription.visit_date.desc()).all()


@router.post("", response_model=schemas.PrescriptionOut)
def create_prescription(
    doctor_name: str = Form(...),
    hospital_name: str = Form(...),
    visit_date: date = Form(...),
    next_visit_date: Optional[date] = Form(None),
    notes: Optional[str] = Form(None),
    prescription_image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user),
):
    image_path = None
    if prescription_image and prescription_image.filename:
        ext = os.path.splitext(prescription_image.filename)[1]
        fname = f"{uuid.uuid4()}{ext}"
        full_path = os.path.join(UPLOAD_DIR, fname)
        with open(full_path, "wb") as f:
            shutil.copyfileobj(prescription_image.file, f)
        image_path = f"/uploads/prescriptions/{fname}"

    presc = models.Prescription(
        user_id=user.id,
        doctor_name=doctor_name,
        hospital_name=hospital_name,
        visit_date=visit_date,
        next_visit_date=next_visit_date,
        notes=notes,
        prescription_image=image_path,
    )
    db.add(presc)
    db.commit()
    db.refresh(presc)
    return presc


@router.get("/{presc_id}", response_model=schemas.PrescriptionOut)
def get_prescription(presc_id: str, db: Session = Depends(get_db), user: models.User = Depends(auth.get_current_user)):
    presc = _scope_query(db, user).filter(models.Prescription.id == presc_id).first()
    if not presc:
        raise HTTPException(status_code=404, detail="Prescription not found")
    return presc


@router.put("/{presc_id}", response_model=schemas.PrescriptionOut)
def update_prescription(presc_id: str, payload: schemas.PrescriptionUpdate, db: Session = Depends(get_db), user: models.User = Depends(auth.get_current_user)):
    presc = _scope_query(db, user).filter(models.Prescription.id == presc_id).first()
    if not presc:
        raise HTTPException(status_code=404, detail="Prescription not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(presc, k, v)
    db.commit()
    db.refresh(presc)
    return presc


@router.delete("/{presc_id}")
def delete_prescription(presc_id: str, db: Session = Depends(get_db), user: models.User = Depends(auth.get_current_user)):
    presc = _scope_query(db, user).filter(models.Prescription.id == presc_id).first()
    if not presc:
        raise HTTPException(status_code=404, detail="Prescription not found")
    db.delete(presc)
    db.commit()
    return {"ok": True}
