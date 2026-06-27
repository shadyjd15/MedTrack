import os
import shutil
import uuid
from datetime import date, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_

from .. import models, schemas, auth
from ..database import get_db

router = APIRouter(prefix="/api/medicines", tags=["medicines"])

UPLOAD_DIR = "uploads/medicines"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def _scope_query(db: Session, user: models.User):
    q = db.query(models.Medicine).join(models.Prescription).options(joinedload(models.Medicine.tags), joinedload(models.Medicine.prescription))
    if user.role != models.RoleEnum.admin:
        q = q.filter(models.Prescription.user_id == user.id)
    return q


def _to_out(m: models.Medicine) -> schemas.MedicineOut:
    out = schemas.MedicineOut.model_validate(m)
    out.doctor_name = m.prescription.doctor_name
    out.hospital_name = m.prescription.hospital_name
    out.visit_date = m.prescription.visit_date
    return out


def _get_or_create_tags(db: Session, tag_names: List[str]) -> List[models.SymptomTag]:
    tags = []
    for raw in tag_names:
        name = raw.strip().lower()
        if not name:
            continue
        tag = db.query(models.SymptomTag).filter(models.SymptomTag.name == name).first()
        if not tag:
            tag = models.SymptomTag(name=name)
            db.add(tag)
            db.flush()
        tags.append(tag)
    return tags


@router.get("", response_model=List[schemas.MedicineOut])
def list_medicines(
    q: Optional[str] = Query(None, description="free text search across name/composition/manufacturer"),
    doctor: Optional[str] = None,
    hospital: Optional[str] = None,
    tag: Optional[str] = None,
    composition: Optional[str] = None,
    active_only: Optional[bool] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user),
):
    query = _scope_query(db, user)

    if q:
        like = f"%{q}%"
        query = query.filter(or_(
            models.Medicine.name.ilike(like),
            models.Medicine.composition.ilike(like),
            models.Medicine.manufacturer.ilike(like),
            models.Prescription.doctor_name.ilike(like),
            models.Prescription.hospital_name.ilike(like),
        ))
    if doctor:
        query = query.filter(models.Prescription.doctor_name.ilike(f"%{doctor}%"))
    if hospital:
        query = query.filter(models.Prescription.hospital_name.ilike(f"%{hospital}%"))
    if composition:
        query = query.filter(models.Medicine.composition.ilike(f"%{composition}%"))
    if active_only is not None:
        query = query.filter(models.Medicine.is_active == active_only)
    if from_date:
        query = query.filter(models.Prescription.visit_date >= from_date)
    if to_date:
        query = query.filter(models.Prescription.visit_date <= to_date)
    if tag:
        query = query.join(models.Medicine.tags).filter(models.SymptomTag.name.ilike(f"%{tag}%"))

    meds = query.order_by(models.Medicine.created_at.desc()).all()
    return [_to_out(m) for m in meds]


@router.get("/by-composition/{composition}", response_model=List[schemas.MedicineOut])
def find_by_composition(composition: str, db: Session = Depends(get_db), user: models.User = Depends(auth.get_current_user)):
    """Find alternate medicines (any user's history visible to admin, own history for users) sharing the same composition."""
    query = _scope_query(db, user).filter(models.Medicine.composition.ilike(f"%{composition}%"))
    meds = query.all()
    return [_to_out(m) for m in meds]


@router.post("", response_model=schemas.MedicineOut)
def create_medicine(
    prescription_id: str = Form(...),
    name: str = Form(...),
    composition: str = Form(...),
    dose: str = Form(...),
    frequency: Optional[str] = Form(None),
    duration_days: Optional[int] = Form(None),
    timing: Optional[str] = Form(None),
    manufacturer: Optional[str] = Form(None),
    start_date: Optional[date] = Form(None),
    end_date: Optional[date] = Form(None),
    is_active: bool = Form(True),
    notes: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),  # comma separated
    photo: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user),
):
    presc = db.query(models.Prescription).filter(models.Prescription.id == prescription_id).first()
    if not presc:
        raise HTTPException(status_code=404, detail="Prescription not found")
    if user.role != models.RoleEnum.admin and presc.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not allowed")

    photo_path = None
    if photo and photo.filename:
        ext = os.path.splitext(photo.filename)[1]
        fname = f"{uuid.uuid4()}{ext}"
        full_path = os.path.join(UPLOAD_DIR, fname)
        with open(full_path, "wb") as f:
            shutil.copyfileobj(photo.file, f)
        photo_path = f"/uploads/medicines/{fname}"

    med = models.Medicine(
        prescription_id=prescription_id,
        name=name,
        composition=composition,
        dose=dose,
        frequency=frequency,
        duration_days=duration_days,
        timing=timing,
        manufacturer=manufacturer,
        start_date=start_date,
        end_date=end_date,
        is_active=is_active,
        notes=notes,
        photo=photo_path,
    )
    if tags:
        med.tags = _get_or_create_tags(db, tags.split(","))

    db.add(med)
    db.commit()
    db.refresh(med)
    return _to_out(med)


@router.get("/{med_id}", response_model=schemas.MedicineOut)
def get_medicine(med_id: str, db: Session = Depends(get_db), user: models.User = Depends(auth.get_current_user)):
    med = _scope_query(db, user).filter(models.Medicine.id == med_id).first()
    if not med:
        raise HTTPException(status_code=404, detail="Medicine not found")
    return _to_out(med)


@router.put("/{med_id}", response_model=schemas.MedicineOut)
def update_medicine(med_id: str, payload: schemas.MedicineUpdate, db: Session = Depends(get_db), user: models.User = Depends(auth.get_current_user)):
    med = _scope_query(db, user).filter(models.Medicine.id == med_id).first()
    if not med:
        raise HTTPException(status_code=404, detail="Medicine not found")
    data = payload.model_dump(exclude_unset=True)
    tag_names = data.pop("tags", None)
    for k, v in data.items():
        setattr(med, k, v)
    if tag_names is not None:
        med.tags = _get_or_create_tags(db, tag_names)
    db.commit()
    db.refresh(med)
    return _to_out(med)


@router.post("/{med_id}/photo", response_model=schemas.MedicineOut)
def upload_photo(med_id: str, photo: UploadFile = File(...), db: Session = Depends(get_db), user: models.User = Depends(auth.get_current_user)):
    med = _scope_query(db, user).filter(models.Medicine.id == med_id).first()
    if not med:
        raise HTTPException(status_code=404, detail="Medicine not found")
    ext = os.path.splitext(photo.filename)[1]
    fname = f"{uuid.uuid4()}{ext}"
    full_path = os.path.join(UPLOAD_DIR, fname)
    with open(full_path, "wb") as f:
        shutil.copyfileobj(photo.file, f)
    med.photo = f"/uploads/medicines/{fname}"
    db.commit()
    db.refresh(med)
    return _to_out(med)


@router.delete("/{med_id}")
def delete_medicine(med_id: str, db: Session = Depends(get_db), user: models.User = Depends(auth.get_current_user)):
    med = _scope_query(db, user).filter(models.Medicine.id == med_id).first()
    if not med:
        raise HTTPException(status_code=404, detail="Medicine not found")
    db.delete(med)
    db.commit()
    return {"ok": True}
