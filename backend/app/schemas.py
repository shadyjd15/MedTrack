from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


CURRENCIES = ["USD", "EUR", "GBP", "SAR", "AED", "EGP", "INR", "PKR", "CAD", "AUD", "JPY"]


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
    theme_preference: Optional[str] = "light"
    currency: Optional[str] = "USD"


# ---------- Users ----------
class UserCreate(BaseModel):
    username: str
    password: str
    full_name: Optional[str] = None
    email: Optional[str] = None
    role: str = "user"  # admin | user | caregiver
    currency: str = "USD"


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None
    theme_preference: Optional[str] = None
    currency: Optional[str] = None
    role: Optional[str] = None


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    username: str
    full_name: Optional[str] = None
    email: Optional[str] = None
    role: str
    is_active: bool
    theme_preference: Optional[str] = "light"
    currency: Optional[str] = "USD"
    created_at: datetime


# ---------- Caregivers ----------
class CaregiverLinkCreate(BaseModel):
    caregiver_id: str
    patient_id: str


class CaregiverLinkOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    caregiver_id: str
    patient_id: str
    caregiver_name: Optional[str] = None
    patient_name: Optional[str] = None


# ---------- Tags ----------
class TagOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str


# ---------- Cost items ----------
class CostItemCreate(BaseModel):
    category: str
    payment_method: str
    amount: float
    description: Optional[str] = None


class CostItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    category: str
    payment_method: str
    amount: float
    description: Optional[str] = None


# ---------- Allergies ----------
class AllergyCreate(BaseModel):
    substance: str
    reaction: Optional[str] = None
    severity: Optional[str] = None
    notes: Optional[str] = None


class AllergyUpdate(BaseModel):
    substance: Optional[str] = None
    reaction: Optional[str] = None
    severity: Optional[str] = None
    notes: Optional[str] = None


class AllergyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    substance: str
    reaction: Optional[str] = None
    severity: Optional[str] = None
    notes: Optional[str] = None


class AllergyCheckResult(BaseModel):
    has_warning: bool
    matched_substance: Optional[str] = None
    severity: Optional[str] = None
    reaction: Optional[str] = None


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
    tags: List[str] = []
    quantity_remaining: Optional[int] = None
    refill_threshold: Optional[int] = None
    cost: Optional[float] = None
    payment_method: Optional[str] = None
    insurance_covered: bool = False


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
    quantity_remaining: Optional[int] = None
    refill_threshold: Optional[int] = None
    cost: Optional[float] = None
    payment_method: Optional[str] = None
    insurance_covered: Optional[bool] = None


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
    quantity_remaining: Optional[int] = None
    refill_threshold: Optional[int] = None
    cost: Optional[float] = None
    payment_method: Optional[str] = None
    insurance_covered: bool = False
    # denormalized, filled manually in router
    doctor_name: Optional[str] = None
    hospital_name: Optional[str] = None
    visit_date: Optional[date] = None
    is_low_stock: bool = False
    allergy_warning: Optional[AllergyCheckResult] = None


class MedicineImportRow(BaseModel):
    doctor_name: str
    hospital_name: str
    visit_date: date
    name: str
    composition: str
    dose: str
    frequency: Optional[str] = None
    manufacturer: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_active: Optional[bool] = True
    tags: Optional[str] = None
    notes: Optional[str] = None


class ImportResult(BaseModel):
    imported: int
    skipped: int
    errors: List[str] = []


# ---------- Lab tests ----------
class LabTestCreate(BaseModel):
    prescription_id: str
    test_name: str
    test_type: str = "lab"
    test_date: Optional[date] = None
    result_summary: Optional[str] = None
    is_completed: bool = False


class LabTestUpdate(BaseModel):
    test_name: Optional[str] = None
    test_type: Optional[str] = None
    test_date: Optional[date] = None
    result_summary: Optional[str] = None
    is_completed: Optional[bool] = None


class LabTestOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    prescription_id: str
    test_name: str
    test_type: str
    test_date: Optional[date] = None
    result_summary: Optional[str] = None
    file_path: Optional[str] = None
    is_completed: bool
    doctor_name: Optional[str] = None
    hospital_name: Optional[str] = None


# ---------- Vaccinations ----------
class VaccinationCreate(BaseModel):
    vaccine_name: str
    dose_number: Optional[int] = None
    date_administered: date
    next_due_date: Optional[date] = None
    administered_at: Optional[str] = None
    batch_number: Optional[str] = None
    notes: Optional[str] = None


class VaccinationUpdate(BaseModel):
    vaccine_name: Optional[str] = None
    dose_number: Optional[int] = None
    date_administered: Optional[date] = None
    next_due_date: Optional[date] = None
    administered_at: Optional[str] = None
    batch_number: Optional[str] = None
    notes: Optional[str] = None


class VaccinationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    vaccine_name: str
    dose_number: Optional[int] = None
    date_administered: date
    next_due_date: Optional[date] = None
    administered_at: Optional[str] = None
    batch_number: Optional[str] = None
    notes: Optional[str] = None
    certificate_file: Optional[str] = None


# ---------- Prescription ----------
class PrescriptionUpdate(BaseModel):
    doctor_name: Optional[str] = None
    hospital_name: Optional[str] = None
    visit_date: Optional[date] = None
    next_visit_date: Optional[date] = None
    diagnosis: Optional[str] = None
    notes: Optional[str] = None
    payment_method: Optional[str] = None
    bp_systolic: Optional[int] = None
    bp_diastolic: Optional[int] = None
    weight_kg: Optional[float] = None
    heart_rate: Optional[int] = None


class PrescriptionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    doctor_name: str
    hospital_name: str
    visit_date: date
    next_visit_date: Optional[date] = None
    diagnosis: Optional[str] = None
    notes: Optional[str] = None
    prescription_image: Optional[str] = None
    payment_method: Optional[str] = None
    bp_systolic: Optional[int] = None
    bp_diastolic: Optional[int] = None
    weight_kg: Optional[float] = None
    heart_rate: Optional[int] = None
    medicines: List[MedicineOut] = []
    cost_items: List[CostItemOut] = []
    lab_tests: List[LabTestOut] = []
    total_cost: float = 0.0


# ---------- Dashboard ----------
class SpendingSummary(BaseModel):
    year: int
    cash_total: float
    insurance_total: float
    grand_total: float
    by_category: dict = {}


class LastVitals(BaseModel):
    recorded_on: Optional[date] = None
    bp_systolic: Optional[int] = None
    bp_diastolic: Optional[int] = None
    weight_kg: Optional[float] = None
    heart_rate: Optional[int] = None


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
    low_stock_medicines: List[MedicineOut] = []
    last_vitals: Optional[LastVitals] = None
    spending: Optional[SpendingSummary] = None
    upcoming_lab_tests: List[LabTestOut] = []
    upcoming_vaccinations: List[VaccinationOut] = []
    currency: str = "USD"


# ---------- OCR ----------
class OcrResult(BaseModel):
    raw_text: str
    guessed_medicine_name: Optional[str] = None
    guessed_composition: Optional[str] = None
    guessed_dose: Optional[str] = None
    guessed_doctor_name: Optional[str] = None
    guessed_hospital_name: Optional[str] = None


# ---------- Version ----------
class VersionInfo(BaseModel):
    version: str
    repo: Optional[str] = None


# ---------- SMTP / email settings ----------
class SmtpSettingsUpdate(BaseModel):
    host: Optional[str] = None
    port: Optional[int] = None
    username: Optional[str] = None
    password: Optional[str] = None
    use_tls: Optional[bool] = None
    from_email: Optional[str] = None
    from_name: Optional[str] = None
    notify_on_account_created: Optional[bool] = None
    notify_on_password_change: Optional[bool] = None


class SmtpSettingsOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    host: Optional[str] = None
    port: Optional[int] = None
    username: Optional[str] = None
    has_password: bool = False
    use_tls: bool = True
    from_email: Optional[str] = None
    from_name: Optional[str] = None
    notify_on_account_created: bool = True
    notify_on_password_change: bool = True


class TestEmailRequest(BaseModel):
    to: str
