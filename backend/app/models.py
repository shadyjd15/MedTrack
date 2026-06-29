import enum
import uuid
from datetime import datetime, date

from sqlalchemy import (
    Column, String, Integer, Boolean, Date, DateTime, ForeignKey,
    Table, Text, Enum, Float, UniqueConstraint
)
from sqlalchemy.orm import relationship
from .database import Base


def gen_uuid():
    return str(uuid.uuid4())


class RoleEnum(str, enum.Enum):
    admin = "admin"
    user = "user"
    caregiver = "caregiver"


# NOTE: payment_method / category / test_type used to be native Postgres ENUM
# columns. They are now plain strings (validated in the Pydantic schemas /
# routers instead) specifically so that adding them to already-deployed
# databases is a trivial ADD COLUMN rather than requiring a CREATE TYPE +
# ALTER TYPE migration. Keep new "choice" fields as String unless you have a
# strong reason not to — see migrations.py for why.

# Many-to-many: medicine <-> symptom tags
medicine_tags = Table(
    "medicine_tags",
    Base.metadata,
    Column("medicine_id", String, ForeignKey("medicines.id"), primary_key=True),
    Column("tag_id", String, ForeignKey("symptom_tags.id"), primary_key=True),
)


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=gen_uuid)
    username = Column(String, unique=True, nullable=False, index=True)
    full_name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(RoleEnum), default=RoleEnum.user, nullable=False)
    is_active = Column(Boolean, default=True)
    theme_preference = Column(String, default="light")  # light | dark
    currency = Column(String, default="USD")  # ISO 4217 code, e.g. USD, EUR, GBP, SAR
    created_at = Column(DateTime, default=datetime.utcnow)

    prescriptions = relationship("Prescription", back_populates="user", cascade="all, delete-orphan")
    vaccinations = relationship("Vaccination", back_populates="user", cascade="all, delete-orphan")
    allergies = relationship("Allergy", back_populates="user", cascade="all, delete-orphan")


class CaregiverLink(Base):
    """Grants a caregiver account access to a patient (regular user) account's records."""
    __tablename__ = "caregiver_links"
    __table_args__ = (UniqueConstraint("caregiver_id", "patient_id", name="uq_caregiver_patient"),)

    id = Column(String, primary_key=True, default=gen_uuid)
    caregiver_id = Column(String, ForeignKey("users.id"), nullable=False)
    patient_id = Column(String, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    caregiver = relationship("User", foreign_keys=[caregiver_id])
    patient = relationship("User", foreign_keys=[patient_id])


class SymptomTag(Base):
    __tablename__ = "symptom_tags"

    id = Column(String, primary_key=True, default=gen_uuid)
    name = Column(String, unique=True, nullable=False, index=True)

    medicines = relationship("Medicine", secondary=medicine_tags, back_populates="tags")


class Prescription(Base):
    """A single doctor visit / prescription event."""
    __tablename__ = "prescriptions"

    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    doctor_name = Column(String, nullable=False, index=True)
    hospital_name = Column(String, nullable=False, index=True)
    visit_date = Column(Date, nullable=False, index=True)
    next_visit_date = Column(Date, nullable=True)
    diagnosis = Column(String, nullable=True, index=True)
    notes = Column(Text, nullable=True)
    prescription_image = Column(String, nullable=True)  # path to uploaded scan/photo

    # Payment / cost
    payment_method = Column(String, nullable=True)  # "cash" | "insurance" — default for the visit

    # Vitals captured during this visit
    bp_systolic = Column(Integer, nullable=True)
    bp_diastolic = Column(Integer, nullable=True)
    weight_kg = Column(Float, nullable=True)
    heart_rate = Column(Integer, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="prescriptions")
    medicines = relationship("Medicine", back_populates="prescription", cascade="all, delete-orphan")
    cost_items = relationship("CostItem", back_populates="prescription", cascade="all, delete-orphan")
    lab_tests = relationship("LabTest", back_populates="prescription", cascade="all, delete-orphan")


class CostItem(Base):
    """Itemized spend for a visit, e.g. reception fee, pharmacy bill, lab fee, x-ray fee."""
    __tablename__ = "cost_items"

    id = Column(String, primary_key=True, default=gen_uuid)
    prescription_id = Column(String, ForeignKey("prescriptions.id"), nullable=False)
    category = Column(String, nullable=False, default="other")
    payment_method = Column(String, nullable=False, default="cash")
    amount = Column(Float, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    prescription = relationship("Prescription", back_populates="cost_items")


class Medicine(Base):
    __tablename__ = "medicines"

    id = Column(String, primary_key=True, default=gen_uuid)
    prescription_id = Column(String, ForeignKey("prescriptions.id"), nullable=False)
    name = Column(String, nullable=False, index=True)
    composition = Column(String, nullable=False, index=True)  # mandatory - active ingredient(s)
    dose = Column(String, nullable=False)  # mandatory e.g. "500mg"
    frequency = Column(String, nullable=True)  # e.g. "Twice a day"
    duration_days = Column(Integer, nullable=True)
    timing = Column(String, nullable=True)  # e.g. "After food"
    manufacturer = Column(String, nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True)  # currently being taken
    photo = Column(String, nullable=True)  # path to medicine photo
    notes = Column(Text, nullable=True)

    # Refill tracking
    quantity_remaining = Column(Integer, nullable=True)
    refill_threshold = Column(Integer, nullable=True)  # alert when remaining <= this

    # Cost / insurance
    cost = Column(Float, nullable=True)
    payment_method = Column(String, nullable=True)
    insurance_covered = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    prescription = relationship("Prescription", back_populates="medicines")
    tags = relationship("SymptomTag", secondary=medicine_tags, back_populates="medicines")


class LabTest(Base):
    """Lab tests / imaging requested by a physician during a visit."""
    __tablename__ = "lab_tests"

    id = Column(String, primary_key=True, default=gen_uuid)
    prescription_id = Column(String, ForeignKey("prescriptions.id"), nullable=False)
    test_name = Column(String, nullable=False)  # e.g. "Complete Blood Count", "Chest X-Ray"
    test_type = Column(String, nullable=False, default="lab")  # "lab" | "imaging"
    test_date = Column(Date, nullable=True)
    result_summary = Column(Text, nullable=True)
    file_path = Column(String, nullable=True)  # link to result file (PDF/image)
    is_completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    prescription = relationship("Prescription", back_populates="lab_tests")


class Vaccination(Base):
    """Vaccination records, tracked separately from prescriptions/visits."""
    __tablename__ = "vaccinations"

    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    vaccine_name = Column(String, nullable=False, index=True)
    dose_number = Column(Integer, nullable=True)  # 1st dose, 2nd dose, booster, etc.
    date_administered = Column(Date, nullable=False)
    next_due_date = Column(Date, nullable=True)
    administered_at = Column(String, nullable=True)  # hospital/clinic
    batch_number = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    certificate_file = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="vaccinations")


class Allergy(Base):
    """Known allergy / adverse reaction to a substance or medicine composition."""
    __tablename__ = "allergies"

    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    substance = Column(String, nullable=False, index=True)  # matched against medicine.composition
    reaction = Column(String, nullable=True)  # e.g. "Rash", "Anaphylaxis"
    severity = Column(String, nullable=True)  # "mild" | "moderate" | "severe"
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="allergies")


class SmtpSettings(Base):
    """Single-row table holding the admin-configured outbound email settings."""
    __tablename__ = "smtp_settings"

    id = Column(String, primary_key=True, default=gen_uuid)
    host = Column(String, nullable=True)
    port = Column(Integer, nullable=True, default=587)
    username = Column(String, nullable=True)
    password = Column(String, nullable=True)
    use_tls = Column(Boolean, default=True)
    from_email = Column(String, nullable=True)
    from_name = Column(String, nullable=True, default="MediCal")
    notify_on_account_created = Column(Boolean, default=True)
    notify_on_password_change = Column(Boolean, default=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
