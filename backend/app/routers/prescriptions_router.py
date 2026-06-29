import os
import json
import shutil
import uuid
from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session, joinedload

from .. import models, schemas, auth
from ..database import get_db

router = APIRouter(prefix="/api/prescriptions", tags=["prescriptions"])

UPLOAD_DIR = "uploads/prescriptions"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def _scope_query(db: Session, scope_user_id: Optional[str]):
    q = db.query(models.Prescription).options(
        joinedload(models.Prescription.cost_items),
        joinedload(models.Prescription.lab_tests),
        joinedload(models.Prescription.medicines),
    )
    if scope_user_id is not None:
        q = q.filter(models.Prescription.user_id == scope_user_id)
    return q


def _enum_val(v):
    return v.value if hasattr(v, "value") else v


def _to_out(p: models.Prescription) -> schemas.PrescriptionOut:
    out = schemas.PrescriptionOut.model_validate(p)
    for m, m_out in zip(p.medicines, out.medicines):
        m_out.doctor_name = p.doctor_name
        m_out.hospital_name = p.hospital_name
        m_out.visit_date = p.visit_date
        m_out.is_low_stock = (
            m.quantity_remaining is not None and m.refill_threshold is not None
            and m.quantity_remaining <= m.refill_threshold
        )
    for lt, lt_out in zip(p.lab_tests, out.lab_tests):
        lt_out.doctor_name = p.doctor_name
        lt_out.hospital_name = p.hospital_name
    out.total_cost = sum(ci.amount for ci in p.cost_items)
    return out


@router.get("", response_model=List[schemas.PrescriptionOut])
def list_prescriptions(
    db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user),
    scope_user_id: Optional[str] = Depends(auth.get_scope_user_id),
):
    rows = _scope_query(db, scope_user_id).order_by(models.Prescription.visit_date.desc()).all()
    return [_to_out(p) for p in rows]


@router.post("", response_model=schemas.PrescriptionOut)
def create_prescription(
    doctor_name: str = Form(...),
    hospital_name: str = Form(...),
    visit_date: date = Form(...),
    next_visit_date: Optional[date] = Form(None),
    diagnosis: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    payment_method: Optional[str] = Form(None),
    bp_systolic: Optional[int] = Form(None),
    bp_diastolic: Optional[int] = Form(None),
    weight_kg: Optional[float] = Form(None),
    heart_rate: Optional[int] = Form(None),
    cost_items: Optional[str] = Form(None),  # JSON list of {category, payment_method, amount, description}
    prescription_image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user),
    scope_user_id: Optional[str] = Depends(auth.get_scope_user_id),
):
    owner_id = scope_user_id if scope_user_id is not None else user.id

    image_path = None
    if prescription_image and prescription_image.filename:
        ext = os.path.splitext(prescription_image.filename)[1]
        fname = f"{uuid.uuid4()}{ext}"
        full_path = os.path.join(UPLOAD_DIR, fname)
        with open(full_path, "wb") as f:
            shutil.copyfileobj(prescription_image.file, f)
        image_path = f"/uploads/prescriptions/{fname}"

    presc = models.Prescription(
        user_id=owner_id,
        doctor_name=doctor_name,
        hospital_name=hospital_name,
        visit_date=visit_date,
        next_visit_date=next_visit_date,
        diagnosis=diagnosis,
        notes=notes,
        prescription_image=image_path,
        payment_method=payment_method or None,
        bp_systolic=bp_systolic,
        bp_diastolic=bp_diastolic,
        weight_kg=weight_kg,
        heart_rate=heart_rate,
    )
    db.add(presc)
    db.flush()

    if cost_items:
        try:
            items = json.loads(cost_items)
        except (json.JSONDecodeError, TypeError):
            items = []
        for item in items:
            if not item.get("amount"):
                continue
            db.add(models.CostItem(
                prescription_id=presc.id,
                category=item.get("category", "other"),
                payment_method=item.get("payment_method", "cash"),
                amount=float(item["amount"]),
                description=item.get("description"),
            ))

    db.commit()
    db.refresh(presc)
    return _to_out(presc)


@router.get("/{presc_id}", response_model=schemas.PrescriptionOut)
def get_prescription(
    presc_id: str, db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user),
    scope_user_id: Optional[str] = Depends(auth.get_scope_user_id),
):
    presc = _scope_query(db, scope_user_id).filter(models.Prescription.id == presc_id).first()
    if not presc:
        raise HTTPException(status_code=404, detail="Prescription not found")
    return _to_out(presc)


@router.put("/{presc_id}", response_model=schemas.PrescriptionOut)
def update_prescription(
    presc_id: str, payload: schemas.PrescriptionUpdate, db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user),
    scope_user_id: Optional[str] = Depends(auth.get_scope_user_id),
):
    presc = _scope_query(db, scope_user_id).filter(models.Prescription.id == presc_id).first()
    if not presc:
        raise HTTPException(status_code=404, detail="Prescription not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(presc, k, v)
    db.commit()
    db.refresh(presc)
    return _to_out(presc)


@router.delete("/{presc_id}")
def delete_prescription(
    presc_id: str, db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user),
    scope_user_id: Optional[str] = Depends(auth.get_scope_user_id),
):
    presc = _scope_query(db, scope_user_id).filter(models.Prescription.id == presc_id).first()
    if not presc:
        raise HTTPException(status_code=404, detail="Prescription not found")
    db.delete(presc)
    db.commit()
    return {"ok": True}


# ---------- Cost items ----------
@router.post("/{presc_id}/cost-items", response_model=schemas.PrescriptionOut)
def add_cost_item(
    presc_id: str, payload: schemas.CostItemCreate, db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user),
    scope_user_id: Optional[str] = Depends(auth.get_scope_user_id),
):
    presc = _scope_query(db, scope_user_id).filter(models.Prescription.id == presc_id).first()
    if not presc:
        raise HTTPException(status_code=404, detail="Prescription not found")
    db.add(models.CostItem(prescription_id=presc.id, **payload.model_dump()))
    db.commit()
    db.refresh(presc)
    return _to_out(presc)


@router.delete("/{presc_id}/cost-items/{item_id}", response_model=schemas.PrescriptionOut)
def delete_cost_item(
    presc_id: str, item_id: str, db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user),
    scope_user_id: Optional[str] = Depends(auth.get_scope_user_id),
):
    presc = _scope_query(db, scope_user_id).filter(models.Prescription.id == presc_id).first()
    if not presc:
        raise HTTPException(status_code=404, detail="Prescription not found")
    item = db.query(models.CostItem).filter(models.CostItem.id == item_id, models.CostItem.prescription_id == presc_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Cost item not found")
    db.delete(item)
    db.commit()
    db.refresh(presc)
    return _to_out(presc)
