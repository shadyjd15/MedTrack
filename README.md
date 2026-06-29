# MediCal

A modern, self-hosted healthcare management platform for individuals and families to securely manage medications, prescriptions, doctor visits, laboratory results, vaccinations, allergies, and healthcare spending.

**Current version: 1.2.0**

## Stack
- **Backend:** FastAPI + SQLAlchemy + PostgreSQL, JWT auth, file uploads on a Docker volume, Tesseract OCR, ReportLab PDF export, smtplib for outbound email.
- **Frontend:** Static HTML/CSS/vanilla JS (no build step) served by Nginx, which reverse-proxies `/api` and `/uploads` to the backend. Light/dark theme, responsive collapsible sidebar (off-canvas drawer on mobile).
- **Deployment:** Docker Compose — 3 services: `db`, `backend`, `frontend`.

## Quick start

```bash
cp .env.example .env
# edit .env — at minimum change SECRET_KEY and the default admin password
docker compose up -d --build
```

Visit **http://localhost:8080**. Log in with the admin credentials from your `.env` (default `admin` / `admin123` if unchanged — change this immediately via Settings).

## Upgrading an existing installation

This is now safe and simple:

```bash
git pull
docker compose up -d --build
```

On every startup the backend runs a generic auto-migration (`app/migrations.py`) that diffs every SQLAlchemy model against what actually exists in the database and adds any missing columns/indexes with safe `ADD COLUMN IF NOT EXISTS` statements — it never alters or drops anything. This is what was missing in 1.1.0, which is why upgrading with existing data previously crashed the backend in a boot loop (`column users.theme_preference does not exist`). That class of bug cannot recur now: every future release that adds a column to an existing table will self-heal on first startup instead of needing a manual `ALTER TABLE` or a full Alembic migration.

New tables (e.g. `allergies`, `caregiver_links`, `smtp_settings` in this release) are created automatically by SQLAlchemy regardless — only columns added to *already-existing* tables needed this extra step.

## What's new in 1.2.0

**Bug fixes**
- Mobile layout: the sidebar no longer overlaps content on small screens — it's now an off-canvas drawer opened with a hamburger button, and KPI cards/tables/forms stack properly below ~840px.
- Login page: logo is centered, the "Welcome to MediCal" heading is always white, and the username/password fields always have black text on a white background — these are now fixed, theme-independent colors so the login screen looks right regardless of the light/dark toggle.
- **Upgrade safety**: see "Upgrading an existing installation" above — this was the root cause of the 502/boot-loop you hit going from 1.0 → 1.1.

**New features**
- **Per-user currency**: set when an admin creates a user, changeable any time from Settings. All cost/spending figures across the dashboard, visits, medicines and reports now render in that currency.
- **Email notifications via SMTP**: admins configure an SMTP server (Gmail, Yahoo, AOL, Outlook, or any provider) under Settings → Email. MediCal sends an email with login details on account creation and a confirmation email when a password changes, plus a "send test email" button. Most providers require an app password if 2FA is on.
- **Better report formatting**: every PDF export now opens with a patient-info table (name, username, email, role) before the data table.
- **Filterable reports**: medication and visit exports (CSV + PDF) can be filtered by doctor, diagnosis, composition, and date range from the Reports page.
- **Allergy / adverse-reaction tracking**: a new Allergies page records substances and reactions; adding or editing a medicine checks its composition against your allergies and shows a live warning, and matching medicines get an allergy badge wherever they're listed.
- **Caregiver role**: admins link a caregiver account to one or more patients under Manage Users → Caregiver assignments. A caregiver who logs in sees a patient switcher in the sidebar; everything they do (visits, medicines, labs, vaccinations, allergies, exports) operates on the selected patient's records, scoped and enforced server-side.
- **Bulk CSV import**: import existing medication history from a CSV file (Medicines page → Import CSV), with a "Download CSV template" link so the expected columns are obvious. Visits are matched or created automatically from the doctor/hospital/date columns.
- **Diagnosis field**: added to doctor visits, shown in the visit list/detail, included in CSV/PDF exports and available as a report filter.

## How it works

1. **Admin** logs in, goes to **Manage Users**, creates accounts for patients, caregivers, or other admins — each with their own currency.
2. A **patient** adds a **Doctor Visit**: doctor, hospital, diagnosis, dates, vitals (BP/weight/heart rate), a default payment method, itemized costs per category, and an optional prescription photo (with OCR auto-fill).
3. Within that visit, medicines are added: name, **composition** and **dose** are mandatory (so "what else has this same composition" can be searched if a brand isn't available), plus frequency, timing, manufacturer, dates, symptom tags, refill quantity/threshold, cost, payment method, insurance flag, and a photo. Compositions are checked against the patient's **Allergies** automatically.
4. **Lab Tests & Imaging**, **Vaccinations**, and **Allergies** are tracked as their own record types, independent of medicines.
5. The **Dashboard** shows totals, last visit, next visit, next medicine, medicines ending soon, last vitals, low-stock medicines, and this year's spending split by cash/insurance — all in the patient's own currency.
6. **Search** filters by keyword, composition, doctor, hospital, symptom tag, status, stock level, and visit date range, plus a one-click "find alternates by composition" lookup.
7. **Reports** exports medicine history, visit history, and yearly spending as CSV or PDF, filterable by doctor/diagnosis/composition/date, with a patient-info header on every PDF.
8. **Caregivers** linked to one or more patients use a sidebar patient switcher; every page and export then operates on the selected patient.
9. **Settings** lets any user change their password, currency, and theme; admins additionally manage all accounts, caregiver assignments, and SMTP/email settings.

Admins see all users' data; caregivers see only their linked patients' data; regular users only see their own.

## Enabling the update checker

Set in `.env`:
```
APP_VERSION=1.2.0
GITHUB_REPO=yourname/your-repo
```
The sidebar calls `https://api.github.com/repos/<GITHUB_REPO>/releases/latest` from the browser and shows an "Update available" pill if the latest tag differs from `APP_VERSION` — clicking it opens the GitHub release page. Tag releases as `v1.2.0`, `v1.3.0`, etc., and bump `APP_VERSION` in `.env` (and the `VERSION` file) with each release.

## Pushing this release to GitHub

This project is already a git repository with the 1.2.0 release committed and tagged locally. To publish it:

```bash
cd medtrack
git remote add origin https://github.com/<yourname>/<your-repo>.git
git push -u origin main
git push origin v1.2.0
```

(If you're updating an existing repo instead of creating a new one, skip `git remote add` and just `git push` / `git push --tags`.) Once pushed, set `GITHUB_REPO=<yourname>/<your-repo>` in your running deployment's `.env` and restart the frontend container — the sidebar will then pick up future releases automatically via the update pill described above.

## Configuring email (SMTP) for Gmail / Yahoo / AOL

All three (and most providers) require an **app password**, not your normal login password, if two-factor authentication is enabled — which it is by default on most accounts now:
- **Gmail**: Google Account → Security → 2-Step Verification → App passwords. Host `smtp.gmail.com`, port `587`, TLS on.
- **Yahoo**: Account Security → Generate app password. Host `smtp.mail.yahoo.com`, port `587`, TLS on.
- **AOL**: Account Security → Generate app password. Host `smtp.aol.com`, port `587`, TLS on.

Enter these under **Settings → Email (admin only)**, then use "Send test email" to confirm before relying on it.

## Project structure
```
medtrack/
├── docker-compose.yml
├── .env.example
├── VERSION
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py
│       ├── database.py
│       ├── models.py
│       ├── schemas.py
│       ├── auth.py            # incl. caregiver scope resolution
│       ├── migrations.py      # generic auto-migration — see "Upgrading" above
│       ├── email_utils.py     # SMTP sending + notification templates
│       └── routers/
│           ├── auth_router.py
│           ├── users_router.py
│           ├── prescriptions_router.py   # visits, cost items, vitals, diagnosis
│           ├── medicines_router.py       # refill tracking, allergy checks, CSV import
│           ├── tags_router.py
│           ├── dashboard_router.py       # spending, vitals, low-stock, currency
│           ├── labtests_router.py
│           ├── vaccinations_router.py
│           ├── allergies_router.py
│           ├── caregivers_router.py      # admin link management + caregiver's patient list
│           ├── smtp_router.py            # admin email settings + test send
│           ├── ocr_router.py
│           ├── export_router.py          # CSV/PDF with filters + patient header
│           └── version_router.py
└── frontend/
    ├── Dockerfile
    ├── nginx.conf
    ├── assets/logo.png
    ├── index.html
    ├── dashboard.html
    ├── medicines.html
    ├── visits.html
    ├── lab-tests.html
    ├── vaccinations.html
    ├── allergies.html
    ├── search.html
    ├── reports.html
    ├── users.html             # incl. caregiver assignment management
    ├── settings.html          # incl. currency + admin email settings
    ├── css/style.css
    └── js/ (api.js, sidebar.js, theme.js)
```

## Feature ideas not yet built

- Dose reminders via push/email notifications, not just dashboard display (the email infra from this release makes this straightforward to add next).
- Admin audit log of who changed what.
- Two-factor authentication for admins.
- Family/household grouping so costs can be rolled up across multiple users.
- Native push notifications / PWA install support for refill and appointment reminders.
- Pharmacy price comparison API integration alongside "find alternates by composition."
- Scheduled/recurring reminder emails (current email support is transactional only: account creation + password change + test email).

## Security notes before production use
- Change `SECRET_KEY` and the default admin password immediately.
- Put this behind HTTPS (e.g. Caddy/Traefik with Let's Encrypt) — it runs plain HTTP by default, fine for local/LAN use only.
- Tighten CORS in `backend/app/main.py` (currently `allow_origins=["*"]`) to your real domain.
- SMTP credentials are stored in plain text in the database — fine for a self-hosted single-admin install, but encrypt the volume/disk if hosting sensitive records, and use an app password (not your main account password) for the SMTP login.
- OCR text and lab/vaccination files are stored unencrypted on the upload volume — encrypt the underlying disk/volume if hosting sensitive records.
