from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas, auth, email_utils
from ..database import get_db

router = APIRouter(prefix="/api/email-settings", tags=["email-settings"])


def _get_or_create(db: Session) -> models.SmtpSettings:
    settings = db.query(models.SmtpSettings).first()
    if not settings:
        settings = models.SmtpSettings()
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings


@router.get("", response_model=schemas.SmtpSettingsOut)
def get_settings(db: Session = Depends(get_db), admin: models.User = Depends(auth.require_admin)):
    settings = _get_or_create(db)
    out = schemas.SmtpSettingsOut.model_validate(settings)
    out.has_password = bool(settings.password)
    return out


@router.put("", response_model=schemas.SmtpSettingsOut)
def update_settings(payload: schemas.SmtpSettingsUpdate, db: Session = Depends(get_db), admin: models.User = Depends(auth.require_admin)):
    settings = _get_or_create(db)
    data = payload.model_dump(exclude_unset=True)
    # An empty string for password means "leave it unchanged" — don't overwrite a saved one accidentally.
    if "password" in data and data["password"] == "":
        data.pop("password")
    for k, v in data.items():
        setattr(settings, k, v)
    db.commit()
    db.refresh(settings)
    out = schemas.SmtpSettingsOut.model_validate(settings)
    out.has_password = bool(settings.password)
    return out


@router.post("/test")
def send_test_email(payload: schemas.TestEmailRequest, db: Session = Depends(get_db), admin: models.User = Depends(auth.require_admin)):
    try:
        email_utils.send_email_or_raise(
            db, payload.to, "MediCal test email",
            "This is a test email from your MediCal installation. If you received this, your SMTP settings are working correctly.",
        )
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=f"Could not send test email: {e}")
    return {"ok": True}
