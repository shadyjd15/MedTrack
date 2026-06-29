from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from .. import models, schemas, auth
from ..database import get_db

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


def _med_to_out(m):
    out = schemas.MedicineOut.model_validate(m)
    out.doctor_name = m.prescription.doctor_name
    out.hospital_name = m.prescription.hospital_name
    out.visit_date = m.prescription.visit_date
    out.is_low_stock = (
        m.quantity_remaining is not None and m.refill_threshold is not None
        and m.quantity_remaining <= m.refill_threshold
    )
    return out


@router.get("/stats", response_model=schemas.DashboardStats)
def get_stats(
    db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user),
    scope_user_id: Optional[str] = Depends(auth.get_scope_user_id),
):
    presc_q = db.query(models.Prescription).options(joinedload(models.Prescription.cost_items))
    med_q = db.query(models.Medicine).join(models.Prescription).options(
        joinedload(models.Medicine.tags), joinedload(models.Medicine.prescription)
    )
    lab_q = db.query(models.LabTest).join(models.Prescription)
    vac_q = db.query(models.Vaccination)

    if scope_user_id is not None:
        presc_q = presc_q.filter(models.Prescription.user_id == scope_user_id)
        med_q = med_q.filter(models.Prescription.user_id == scope_user_id)
        lab_q = lab_q.filter(models.Prescription.user_id == scope_user_id)
        vac_q = vac_q.filter(models.Vaccination.user_id == scope_user_id)

    # Determine which currency to display: the scoped patient's own preference,
    # falling back to the logged-in user's (covers the admin "sees everyone" case).
    currency = user.currency or "USD"
    if scope_user_id is not None and scope_user_id != user.id:
        patient = db.query(models.User).filter(models.User.id == scope_user_id).first()
        if patient and patient.currency:
            currency = patient.currency

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

    all_meds = med_q.all()
    low_stock = [
        m for m in all_meds
        if m.quantity_remaining is not None and m.refill_threshold is not None and m.quantity_remaining <= m.refill_threshold
    ][:8]

    vitals_visit = (
        presc_q.filter(
            (models.Prescription.bp_systolic.isnot(None)) |
            (models.Prescription.weight_kg.isnot(None)) |
            (models.Prescription.heart_rate.isnot(None))
        )
        .order_by(models.Prescription.visit_date.desc())
        .first()
    )
    last_vitals = None
    if vitals_visit:
        last_vitals = schemas.LastVitals(
            recorded_on=vitals_visit.visit_date,
            bp_systolic=vitals_visit.bp_systolic,
            bp_diastolic=vitals_visit.bp_diastolic,
            weight_kg=vitals_visit.weight_kg,
            heart_rate=vitals_visit.heart_rate,
        )

    year = date.today().year
    cash_total = 0.0
    insurance_total = 0.0
    by_category = {}
    for p in presc_q.filter(func.extract("year", models.Prescription.visit_date) == year).all():
        for c in p.cost_items:
            amt = c.amount
            if c.payment_method == "insurance":
                insurance_total += amt
            else:
                cash_total += amt
            by_category[c.category] = by_category.get(c.category, 0) + amt

    spending = schemas.SpendingSummary(
        year=year, cash_total=cash_total, insurance_total=insurance_total,
        grand_total=cash_total + insurance_total, by_category=by_category,
    )

    upcoming_labs = (
        lab_q.filter(models.LabTest.is_completed == False)  # noqa: E712
        .order_by(models.LabTest.test_date.asc().nullslast())
        .limit(5)
        .all()
    )
    upcoming_labs_out = []
    for lt in upcoming_labs:
        out = schemas.LabTestOut.model_validate(lt)
        out.doctor_name = lt.prescription.doctor_name
        out.hospital_name = lt.prescription.hospital_name
        upcoming_labs_out.append(out)

    upcoming_vacs = (
        vac_q.filter(models.Vaccination.next_due_date.isnot(None))
        .filter(models.Vaccination.next_due_date >= date.today())
        .order_by(models.Vaccination.next_due_date.asc())
        .limit(5)
        .all()
    )

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
        medicines_ending_soon=[_med_to_out(m) for m in ending_soon],
        low_stock_medicines=[_med_to_out(m) for m in low_stock],
        last_vitals=last_vitals,
        spending=spending,
        upcoming_lab_tests=upcoming_labs_out,
        upcoming_vaccinations=list(upcoming_vacs),
        currency=currency,
    )
