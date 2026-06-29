"""
Outbound email via admin-configured SMTP settings (stored in the smtp_settings
table). Supports any standard SMTP provider — Gmail, Yahoo, AOL, Outlook,
a company mail server, etc. Gmail/Yahoo/AOL all require an "app password"
rather than your normal login password if 2FA is enabled, which is true for
most accounts today.

This module never raises out of send_email() for notification call-sites —
a failed notification email should never break account creation or password
changes. Use send_email_or_raise() for the explicit "send test email" action
where the admin wants to see the real error.
"""

import logging
import smtplib
from email.mime.text import MIMEText
from sqlalchemy.orm import Session

from . import models

logger = logging.getLogger("medical.email")


def get_settings(db: Session) -> "models.SmtpSettings | None":
    return db.query(models.SmtpSettings).first()


def _send(settings: "models.SmtpSettings", to: str, subject: str, body: str):
    if not settings or not settings.host or not settings.from_email:
        raise RuntimeError("SMTP is not configured yet. Set it up under Settings → Email (admin only).")

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = f'{settings.from_name or "MediCal"} <{settings.from_email}>'
    msg["To"] = to

    port = settings.port or 587
    with smtplib.SMTP(settings.host, port, timeout=15) as server:
        if settings.use_tls:
            server.starttls()
        if settings.username and settings.password:
            server.login(settings.username, settings.password)
        server.sendmail(settings.from_email, [to], msg.as_string())


def send_email_or_raise(db: Session, to: str, subject: str, body: str):
    settings = get_settings(db)
    _send(settings, to, subject, body)


def send_email(db: Session, to: str, subject: str, body: str):
    """Best-effort send — logs and swallows errors so notifications never break the main action."""
    if not to:
        return
    try:
        settings = get_settings(db)
        if not settings or not settings.host:
            return  # SMTP not configured — silently skip, this is expected for most installs
        _send(settings, to, subject, body)
    except Exception as e:  # noqa: BLE001
        logger.warning(f"[email] Failed to send '{subject}' to {to}: {e}")


def notify_account_created(db: Session, to: str, username: str, password: str, full_name: str = ""):
    settings = get_settings(db)
    if not settings or not settings.notify_on_account_created:
        return
    name = full_name or username
    body = (
        f"Hi {name},\n\n"
        f"An account has been created for you on MediCal.\n\n"
        f"Username: {username}\n"
        f"Temporary password: {password}\n\n"
        f"Please sign in and change your password from Settings as soon as possible.\n\n"
        f"— MediCal"
    )
    send_email(db, to, "Your MediCal account has been created", body)


def notify_password_changed(db: Session, to: str, username: str):
    settings = get_settings(db)
    if not settings or not settings.notify_on_password_change:
        return
    body = (
        f"Hi {username},\n\n"
        f"This is a confirmation that the password for your MediCal account was just changed.\n"
        f"If you didn't make this change, contact your administrator immediately.\n\n"
        f"— MediCal"
    )
    send_email(db, to, "Your MediCal password was changed", body)
