from datetime import date
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from .. import models, schemas, auth
from ..database import get_db

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=schemas.DashboardStats)
def get_stats(db: Session = Depends(get_db), user: models.User = Depends(auth.get_current_user)):
    presc_q = db.query(models.Prescription)
    med_q = db.query(models.Medicine).join(models.Prescription).options(
        joinedload(models.Medicine.tags), joinedload(models.Medicine.prescription)
    )
    if user.role != models.RoleEnum.admin:
        presc_q = presc_q.filter(models.Prescription.user_id == user.id)
        med_q = med_q.filter(models.Prescription.user_id == user.id)

    total_medicines = med_q.count()
    active_medicines = med_q.filter(models.Medicine.is_active == True).count()  # noqa: E712
    total_visits = presc_q.count()
    distinct_doctors = presc_q.with_entities(func.count(func.distinct(models.Prescription.doctor_name))).scalar() or 0
    distinct_hospitals = presc_q.with_entities(func.count(func.distinct(models.Prescription.hospital_name))).scalar() or 0

    last_visit = presc_q.order_by(models.Prescription.visit_date.desc()).first()
    next_visit = (
        presc_q.filter(models.Prescription.next_visit_date >= date.today())
        .order_by(models.Prescription.next_visit_date.asc())
        .first()
    )

    next_med = (
        med_q.filter(models.Medicine.is_active == True)  # noqa: E712
        .order_by(models.Medicine.created_at.desc())
        .first()
    )

    ending_soon = (
        med_q.filter(models.Medicine.is_active == True)  # noqa: E712
        .filter(models.Medicine.end_date.isnot(None))
        .filter(models.Medicine.end_date >= date.today())
        .order_by(models.Medicine.end_date.asc())
        .limit(5)
        .all()
    )

    def to_out(m):
        out = schemas.MedicineOut.model_validate(m)
        out.doctor_name = m.prescription.doctor_name
        out.hospital_name = m.prescription.hospital_name
        out.visit_date = m.prescription.visit_date
        return out

    return schemas.DashboardStats(
        total_medicines=total_medicines,
        active_medicines=active_medicines,
        total_hospital_visits=total_visits,
        last_visit_date=last_visit.visit_date if last_visit else None,
        last_visit_doctor=last_visit.doctor_name if last_visit else None,
        next_visit_date=next_visit.next_visit_date if next_visit else None,
        next_medicine_name=next_med.name if next_med else None,
        next_medicine_time=next_med.timing if next_med else None,
        distinct_doctors=distinct_doctors,
        distinct_hospitals=distinct_hospitals,
        medicines_ending_soon=[to_out(m) for m in ending_soon],
    )
