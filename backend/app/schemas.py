from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


# ---------- Auth ----------
class LoginRequest(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    username: str
    full_name: Optional[str] = None
    user_id: str


# ---------- Users ----------
class UserCreate(BaseModel):
    username: str
    password: str
    full_name: Optional[str] = None
    email: Optional[str] = None
    role: str = "user"  # admin can set "admin" or "user"


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    username: str
    full_name: Optional[str] = None
    email: Optional[str] = None
    role: str
    is_active: bool
    created_at: datetime


# ---------- Tags ----------
class TagOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str


# ---------- Medicine ----------
class MedicineCreate(BaseModel):
    prescription_id: str
    name: str
    composition: str
    dose: str
    frequency: Optional[str] = None
    duration_days: Optional[int] = None
    timing: Optional[str] = None
    manufacturer: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_active: bool = True
    notes: Optional[str] = None
    tags: List[str] = []  # tag names


class MedicineUpdate(BaseModel):
    name: Optional[str] = None
    composition: Optional[str] = None
    dose: Optional[str] = None
    frequency: Optional[str] = None
    duration_days: Optional[int] = None
    timing: Optional[str] = None
    manufacturer: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None


class MedicineOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    prescription_id: str
    name: str
    composition: str
    dose: str
    frequency: Optional[str] = None
    duration_days: Optional[int] = None
    timing: Optional[str] = None
    manufacturer: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_active: bool
    photo: Optional[str] = None
    notes: Optional[str] = None
    tags: List[TagOut] = []
    # denormalized, filled manually in router
    doctor_name: Optional[str] = None
    hospital_name: Optional[str] = None
    visit_date: Optional[date] = None


# ---------- Prescription ----------
class PrescriptionCreate(BaseModel):
    doctor_name: str
    hospital_name: str
    visit_date: date
    next_visit_date: Optional[date] = None
    notes: Optional[str] = None


class PrescriptionUpdate(BaseModel):
    doctor_name: Optional[str] = None
    hospital_name: Optional[str] = None
    visit_date: Optional[date] = None
    next_visit_date: Optional[date] = None
    notes: Optional[str] = None


class PrescriptionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    doctor_name: str
    hospital_name: str
    visit_date: date
    next_visit_date: Optional[date] = None
    notes: Optional[str] = None
    prescription_image: Optional[str] = None
    medicines: List[MedicineOut] = []


# ---------- Dashboard ----------
class DashboardStats(BaseModel):
    total_medicines: int
    active_medicines: int
    total_hospital_visits: int
    last_visit_date: Optional[date] = None
    last_visit_doctor: Optional[str] = None
    next_visit_date: Optional[date] = None
    next_medicine_name: Optional[str] = None
    next_medicine_time: Optional[str] = None
    distinct_doctors: int
    distinct_hospitals: int
    medicines_ending_soon: List[MedicineOut] = []
