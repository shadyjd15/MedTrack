import enum
import uuid
from datetime import datetime, date

from sqlalchemy import (
    Column, String, Integer, Boolean, Date, DateTime, ForeignKey,
    Table, Text, Enum
)
from sqlalchemy.orm import relationship
from .database import Base


def gen_uuid():
    return str(uuid.uuid4())


class RoleEnum(str, enum.Enum):
    admin = "admin"
    user = "user"


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
    created_at = Column(DateTime, default=datetime.utcnow)

    prescriptions = relationship("Prescription", back_populates="user", cascade="all, delete-orphan")


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
    notes = Column(Text, nullable=True)
    prescription_image = Column(String, nullable=True)  # path to uploaded scan/photo
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="prescriptions")
    medicines = relationship("Medicine", back_populates="prescription", cascade="all, delete-orphan")


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
    created_at = Column(DateTime, default=datetime.utcnow)

    prescription = relationship("Prescription", back_populates="medicines")
    tags = relationship("SymptomTag", secondary=medicine_tags, back_populates="medicines")
