import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .database import Base, engine, SessionLocal
from . import models, auth
from .routers import auth_router, users_router, prescriptions_router, medicines_router, tags_router, dashboard_router

os.makedirs("uploads/medicines", exist_ok=True)
os.makedirs("uploads/prescriptions", exist_ok=True)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="MedTrack API")

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


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.on_event("startup")
def seed_admin():
    """Create a default admin account on first run if none exists."""
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
            print(f"[seed] Created default admin user '{default_user}' — please change the password after first login.")
    finally:
        db.close()
