import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .database import Base, engine, SessionLocal
from . import models, auth
from .migrations import run_auto_migration
from .routers import (
    auth_router, users_router, prescriptions_router, medicines_router,
    tags_router, dashboard_router, labtests_router, vaccinations_router,
    ocr_router, export_router, version_router, allergies_router,
    caregivers_router, smtp_router,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("medical.startup")

for d in ["uploads/medicines", "uploads/prescriptions", "uploads/lab_tests", "uploads/vaccinations"]:
    os.makedirs(d, exist_ok=True)

# 1. Create any brand-new tables.
Base.metadata.create_all(bind=engine)
# 2. Add any columns that are new on existing tables (safe on data-bearing DBs).
#    See app/migrations.py for why this approach was chosen over Alembic.
run_auto_migration(engine, Base)

app = FastAPI(title="MediCal API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(auth_router.router)
app.include_router(users_router.router)
app.include_router(prescriptions_router.router)
app.include_router(medicines_router.router)
app.include_router(tags_router.router)
app.include_router(dashboard_router.router)
app.include_router(labtests_router.router)
app.include_router(vaccinations_router.router)
app.include_router(ocr_router.router)
app.include_router(export_router.router)
app.include_router(version_router.router)
app.include_router(allergies_router.router)
app.include_router(caregivers_router.router)
app.include_router(smtp_router.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.on_event("startup")
def seed_admin():
    db = SessionLocal()
    try:
        admin_exists = db.query(models.User).filter(models.User.role == models.RoleEnum.admin).first()
        if not admin_exists:
            default_user = os.getenv("DEFAULT_ADMIN_USERNAME", "admin")
            default_pass = os.getenv("DEFAULT_ADMIN_PASSWORD", "admin123")
            admin = models.User(
                username=default_user,
                hashed_password=auth.hash_password(default_pass),
                full_name="Administrator",
                role=models.RoleEnum.admin,
            )
            db.add(admin)
            db.commit()
            logger.info(f"[seed] Created default admin user '{default_user}' — please change the password after first login.")
    finally:
        db.close()
