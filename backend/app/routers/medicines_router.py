import os
import shutil
import uuid
from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_

from .. import models, schemas, auth
from ..database import get_db

router = APIRouter(prefix="/api/medicines", tags=["medicines"])

UPLOAD_DIR = "uploads/medicines"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def _scope_query(db: Session, scope_user_id: Optional[str]):
    q = db.query(models.Medicine).join(models.Prescription).options(joinedload(models.Medicine.tags), joinedload(models.Medicine.prescription))
    if scope_user_id is not None:
        q = q.filter(models.Prescription.user_id == scope_user_id)
    return q


def _check_allergy(db: Session, owner_user_id: str, composition: str) -> Optional[schemas.AllergyCheckResult]:
    if not composition:
        return None
    allergies = db.query(models.Allergy).filter(models.Allergy.user_id == owner_user_id).all()
    comp_lower = composition.lower()
    for a in allergies:
        if a.substance.lower() in comp_lower or comp_lower in a.substance.lower():
            return schemas.AllergyCheckResult(
                has_warning=True, matched_substance=a.substance, severity=a.severity, reaction=a.reaction
            )
    return None


def _to_out(m: models.Medicine, db: Optional[Session] = None) -> schemas.MedicineOut:
    out = schemas.MedicineOut.model_validate(m)
    out.doctor_name = m.prescription.doctor_name
    out.hospital_name = m.prescription.hospital_name
    out.visit_date = m.prescription.visit_date
    out.is_low_stock = (
        m.quantity_remaining is not None and m.refill_threshold is not None
        and m.quantity_remaining <= m.refill_threshold
    )
    if db is not None:
        out.allergy_warning = _check_allergy(db, m.prescription.user_id, m.composition)
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
    q: Optional[str] = Query(None),
    doctor: Optional[str] = None,
    hospital: Optional[str] = None,
    tag: Optional[str] = None,
    composition: Optional[str] = None,
    active_only: Optional[bool] = None,
    low_stock_only: Optional[bool] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user),
    scope_user_id: Optional[str] = Depends(auth.get_scope_user_id),
):
    query = _scope_query(db, scope_user_id)

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
    out = [_to_out(m, db) for m in meds]
    if low_stock_only:
        out = [m for m in out if m.is_low_stock]
    return out


@router.get("/by-composition/{composition}", response_model=List[schemas.MedicineOut])
def find_by_composition(
    composition: str, db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user),
    scope_user_id: Optional[str] = Depends(auth.get_scope_user_id),
):
    query = _scope_query(db, scope_user_id).filter(models.Medicine.composition.ilike(f"%{composition}%"))
    meds = query.all()
    return [_to_out(m, db) for m in meds]


@router.get("/allergy-check", response_model=schemas.AllergyCheckResult)
def allergy_check(
    composition: str,
    db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user),
    scope_user_id: Optional[str] = Depends(auth.get_scope_user_id),
):
    owner_id = scope_user_id if scope_user_id is not None else user.id
    result = _check_allergy(db, owner_id, composition)
    return result or schemas.AllergyCheckResult(has_warning=False)


@router.get("/import/template")
def download_import_template():
    from fastapi.responses import StreamingResponse
    import io
    buf = io.StringIO()
    buf.write("doctor_name,hospital_name,visit_date,name,composition,dose,frequency,manufacturer,start_date,end_date,is_active,tags,notes\n")
    buf.write('Dr. Jane Doe,City General Hospital,2026-01-15,Amoxicillin,Amoxicillin 500mg,1 capsule,Three times a day,Pharma Co,2026-01-15,2026-01-22,false,"infection, throat",Take with food\n')
    buf.seek(0)
    return StreamingResponse(iter([buf.getvalue()]), media_type="text/csv",
                              headers={"Content-Disposition": "attachment; filename=medicine-import-template.csv"})


@router.post("/import", response_model=schemas.ImportResult)
def import_medicines(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user),
    scope_user_id: Optional[str] = Depends(auth.get_scope_user_id),
):
    import csv
    import io as _io

    owner_id = scope_user_id if scope_user_id is not None else user.id
    raw = file.file.read().decode("utf-8-sig", errors="replace")
    reader = csv.DictReader(_io.StringIO(raw))

    required = {"doctor_name", "hospital_name", "visit_date", "name", "composition", "dose"}
    if not required.issubset(set(h.strip() for h in (reader.fieldnames or []))):
        missing = required - set(h.strip() for h in (reader.fieldnames or []))
        raise HTTPException(status_code=400, detail=f"CSV is missing required column(s): {', '.join(missing)}")

    presc_cache = {}  # (doctor, hospital, visit_date) -> Prescription
    imported, skipped, errors = 0, 0, []

    for i, row in enumerate(reader, start=2):  # row 1 is the header
        try:
            doctor = (row.get("doctor_name") or "").strip()
            hospital = (row.get("hospital_name") or "").strip()
            visit_date_str = (row.get("visit_date") or "").strip()
            name = (row.get("name") or "").strip()
            composition = (row.get("composition") or "").strip()
            dose = (row.get("dose") or "").strip()
            if not all([doctor, hospital, visit_date_str, name, composition, dose]):
                skipped += 1
                errors.append(f"Row {i}: missing a required field — skipped")
                continue

            visit_date_parsed = date.fromisoformat(visit_date_str)
            key = (doctor, hospital, visit_date_parsed)
            presc = presc_cache.get(key)
            if not presc:
                presc = db.query(models.Prescription).filter(
                    models.Prescription.user_id == owner_id,
                    models.Prescription.doctor_name == doctor,
                    models.Prescription.hospital_name == hospital,
                    models.Prescription.visit_date == visit_date_parsed,
                ).first()
                if not presc:
                    presc = models.Prescription(
                        user_id=owner_id, doctor_name=doctor, hospital_name=hospital, visit_date=visit_date_parsed,
                    )
                    db.add(presc)
                    db.flush()
                presc_cache[key] = presc

            start_date_val = date.fromisoformat(row["start_date"]) if row.get("start_date") else None
            end_date_val = date.fromisoformat(row["end_date"]) if row.get("end_date") else None
            is_active_val = str(row.get("is_active", "true")).strip().lower() not in ("false", "0", "no", "")

            med = models.Medicine(
                prescription_id=presc.id,
                name=name,
                composition=composition,
                dose=dose,
                frequency=(row.get("frequency") or None),
                manufacturer=(row.get("manufacturer") or None),
                start_date=start_date_val,
                end_date=end_date_val,
                is_active=is_active_val,
                notes=(row.get("notes") or None),
            )
            tags_str = (row.get("tags") or "").strip()
            if tags_str:
                med.tags = _get_or_create_tags(db, tags_str.split(","))
            db.add(med)
            imported += 1
        except Exception as e:  # noqa: BLE001
            skipped += 1
            errors.append(f"Row {i}: {e}")

    db.commit()
    return schemas.ImportResult(imported=imported, skipped=skipped, errors=errors[:25])


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
    tags: Optional[str] = Form(None),
    quantity_remaining: Optional[int] = Form(None),
    refill_threshold: Optional[int] = Form(None),
    cost: Optional[float] = Form(None),
    payment_method: Optional[str] = Form(None),
    insurance_covered: bool = Form(False),
    photo: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user),
    scope_user_id: Optional[str] = Depends(auth.get_scope_user_id),
):
    presc = db.query(models.Prescription).filter(models.Prescription.id == prescription_id).first()
    if not presc:
        raise HTTPException(status_code=404, detail="Prescription not found")
    owner_id = scope_user_id if scope_user_id is not None else user.id
    if scope_user_id is not None and presc.user_id != owner_id:
        raise HTTPException(status_code=403, detail="Not allowed")
    if scope_user_id is None and user.role != models.RoleEnum.admin and presc.user_id != user.id:
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
        quantity_remaining=quantity_remaining,
        refill_threshold=refill_threshold,
        cost=cost,
        payment_method=payment_method or None,
        insurance_covered=insurance_covered,
    )
    if tags:
        med.tags = _get_or_create_tags(db, tags.split(","))

    db.add(med)
    db.commit()
    db.refresh(med)
    return _to_out(med, db)


@router.get("/{med_id}", response_model=schemas.MedicineOut)
def get_medicine(
    med_id: str, db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user),
    scope_user_id: Optional[str] = Depends(auth.get_scope_user_id),
):
    med = _scope_query(db, scope_user_id).filter(models.Medicine.id == med_id).first()
    if not med:
        raise HTTPException(status_code=404, detail="Medicine not found")
    return _to_out(med, db)


@router.put("/{med_id}", response_model=schemas.MedicineOut)
def update_medicine(
    med_id: str, payload: schemas.MedicineUpdate, db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user),
    scope_user_id: Optional[str] = Depends(auth.get_scope_user_id),
):
    med = _scope_query(db, scope_user_id).filter(models.Medicine.id == med_id).first()
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
    return _to_out(med, db)


@router.post("/{med_id}/refill", response_model=schemas.MedicineOut)
def adjust_refill(
    med_id: str, payload: dict, db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user),
    scope_user_id: Optional[str] = Depends(auth.get_scope_user_id),
):
    med = _scope_query(db, scope_user_id).filter(models.Medicine.id == med_id).first()
    if not med:
        raise HTTPException(status_code=404, detail="Medicine not found")
    if "quantity_remaining" in payload:
        med.quantity_remaining = int(payload["quantity_remaining"])
    elif "delta" in payload:
        current = med.quantity_remaining or 0
        med.quantity_remaining = max(0, current + int(payload["delta"]))
    db.commit()
    db.refresh(med)
    return _to_out(med, db)


@router.post("/{med_id}/photo", response_model=schemas.MedicineOut)
def upload_photo(
    med_id: str, photo: UploadFile = File(...), db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user),
    scope_user_id: Optional[str] = Depends(auth.get_scope_user_id),
):
    med = _scope_query(db, scope_user_id).filter(models.Medicine.id == med_id).first()
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
    return _to_out(med, db)


@router.delete("/{med_id}")
def delete_medicine(
    med_id: str, db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user),
    scope_user_id: Optional[str] = Depends(auth.get_scope_user_id),
):
    med = _scope_query(db, scope_user_id).filter(models.Medicine.id == med_id).first()
    if not med:
        raise HTTPException(status_code=404, detail="Medicine not found")
    db.delete(med)
    db.commit()
    return {"ok": True}
