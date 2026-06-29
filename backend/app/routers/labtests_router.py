import os
import shutil
import uuid
from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from .. import models, schemas, auth
from ..database import get_db

router = APIRouter(prefix="/api/lab-tests", tags=["lab-tests"])

UPLOAD_DIR = "uploads/lab_tests"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def _scope_query(db: Session, scope_user_id: Optional[str]):
    q = db.query(models.LabTest).join(models.Prescription)
    if scope_user_id is not None:
        q = q.filter(models.Prescription.user_id == scope_user_id)
    return q


def _to_out(lt: models.LabTest) -> schemas.LabTestOut:
    out = schemas.LabTestOut.model_validate(lt)
    out.doctor_name = lt.prescription.doctor_name
    out.hospital_name = lt.prescription.hospital_name
    return out


@router.get("", response_model=List[schemas.LabTestOut])
def list_lab_tests(
    db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user),
    scope_user_id: Optional[str] = Depends(auth.get_scope_user_id),
):
    rows = _scope_query(db, scope_user_id).order_by(models.LabTest.test_date.desc().nullslast()).all()
    return [_to_out(r) for r in rows]


@router.post("", response_model=schemas.LabTestOut)
def create_lab_test(
    prescription_id: str = Form(...),
    test_name: str = Form(...),
    test_type: str = Form("lab"),
    test_date: Optional[date] = Form(None),
    result_summary: Optional[str] = Form(None),
    is_completed: bool = Form(False),
    result_file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user),
    scope_user_id: Optional[str] = Depends(auth.get_scope_user_id),
):
    presc = db.query(models.Prescription).filter(models.Prescription.id == prescription_id).first()
    if not presc:
        raise HTTPException(status_code=404, detail="Visit not found")
    if scope_user_id is not None and presc.user_id != scope_user_id:
        raise HTTPException(status_code=403, detail="Not allowed")
    if scope_user_id is None and user.role != models.RoleEnum.admin and presc.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not allowed")

    file_path = None
    if result_file and result_file.filename:
        ext = os.path.splitext(result_file.filename)[1]
        fname = f"{uuid.uuid4()}{ext}"
        full_path = os.path.join(UPLOAD_DIR, fname)
        with open(full_path, "wb") as f:
            shutil.copyfileobj(result_file.file, f)
        file_path = f"/uploads/lab_tests/{fname}"

    lt = models.LabTest(
        prescription_id=prescription_id,
        test_name=test_name,
        test_type=test_type,
        test_date=test_date,
        result_summary=result_summary,
        is_completed=is_completed,
        file_path=file_path,
    )
    db.add(lt)
    db.commit()
    db.refresh(lt)
    return _to_out(lt)


@router.put("/{lt_id}", response_model=schemas.LabTestOut)
def update_lab_test(
    lt_id: str, payload: schemas.LabTestUpdate, db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user),
    scope_user_id: Optional[str] = Depends(auth.get_scope_user_id),
):
    lt = _scope_query(db, scope_user_id).filter(models.LabTest.id == lt_id).first()
    if not lt:
        raise HTTPException(status_code=404, detail="Lab test not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(lt, k, v)
    db.commit()
    db.refresh(lt)
    return _to_out(lt)


@router.post("/{lt_id}/file", response_model=schemas.LabTestOut)
def upload_result_file(
    lt_id: str, result_file: UploadFile = File(...), db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user),
    scope_user_id: Optional[str] = Depends(auth.get_scope_user_id),
):
    lt = _scope_query(db, scope_user_id).filter(models.LabTest.id == lt_id).first()
    if not lt:
        raise HTTPException(status_code=404, detail="Lab test not found")
    ext = os.path.splitext(result_file.filename)[1]
    fname = f"{uuid.uuid4()}{ext}"
    full_path = os.path.join(UPLOAD_DIR, fname)
    with open(full_path, "wb") as f:
        shutil.copyfileobj(result_file.file, f)
    lt.file_path = f"/uploads/lab_tests/{fname}"
    db.commit()
    db.refresh(lt)
    return _to_out(lt)


@router.delete("/{lt_id}")
def delete_lab_test(
    lt_id: str, db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user),
    scope_user_id: Optional[str] = Depends(auth.get_scope_user_id),
):
    lt = _scope_query(db, scope_user_id).filter(models.LabTest.id == lt_id).first()
    if not lt:
        raise HTTPException(status_code=404, detail="Lab test not found")
    db.delete(lt)
    db.commit()
    return {"ok": True}
