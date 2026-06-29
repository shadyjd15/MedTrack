# Changelog

All notable changes to MediCal are documented here. Dates reflect when the
change was made, not necessarily a tagged GitHub release.

## [Unreleased]

### Changed
- Settings page reorganized into a responsive grid instead of a single
  narrow column — the compact cards (Profile, App, Appearance, Currency)
  now sit side by side instead of stacking with large empty margins, and
  Change Password / Email (SMTP) sit in a two-column row on wide screens.
- Added `CHANGELOG.md` (this file) — maintained going forward with every change.

## [1.2.0]

### Fixed
- **Upgrade crash on existing databases**: added a generic auto-migration
  (`backend/app/migrations.py`) that runs on every startup, diffs every
  SQLAlchemy model against the live database, and adds any missing
  columns/indexes with safe `ADD COLUMN IF NOT EXISTS` statements. This is
  what was missing in 1.1.0 — upgrading with existing data previously
  crashed the backend in a boot loop (`column users.theme_preference does
  not exist`). `git pull && docker compose up -d --build` is now safe.
- Mobile layout: replaced the broken fixed-position sidebar (which
  overlapped page content on narrow viewports) with a proper off-canvas
  drawer opened via a hamburger button; forms, tables, and the KPI grid now
  stack correctly below ~840px.
- Login page: centered the logo, forced the "Welcome to MediCal" heading to
  always render white, and the username/password fields to always render
  black-on-white — these are now fixed, theme-independent colors instead of
  inheriting dark-mode variables that made them unreadable.

### Added
- Per-user **currency** (set at account creation, changeable in Settings);
  all cost/spending figures across the dashboard, visits, medicines, and
  reports render in that currency.
- **Email notifications via SMTP** — admins configure any provider (Gmail,
  Yahoo, AOL, Outlook, etc.) under Settings → Email. Sends an email with
  login details on account creation and a confirmation on password change,
  plus a "send test email" action.
- **Patient-info header table** on every PDF export (name, username, email,
  role) above the data table.
- **Filterable reports** — medication and visit exports (CSV + PDF) can be
  filtered by doctor, diagnosis, composition, and date range from Reports.
- **Allergy / adverse-reaction tracking** — new Allergies page; adding or
  editing a medicine checks its composition against recorded allergies and
  shows a live warning, with a badge on matching medicines wherever listed.
- **Caregiver role** — admins link a caregiver account to one or more
  patients (Manage Users → Caregiver assignments); caregivers get a patient
  switcher in the sidebar, and all data access is scoped server-side to the
  selected patient via an `X-Patient-Id` header.
- **Bulk CSV import** of existing medication history (Medicines → Import
  CSV), with a "Download CSV template" link. Visits are matched or created
  automatically from the doctor/hospital/date columns.
- **Diagnosis field** on doctor visits — shown in the visit list/detail,
  included in exports, and available as a report filter.
- Android support:
  - PWA: `manifest.json`, generated icon set (incl. maskable), service
    worker (cache-first for static shell assets, network-first/passthrough
    for `/api/` and `/uploads/` so medical data is never served stale), and
    an explicit "Install app" button under Settings → App.
  - `android-app/`: a Capacitor project scaffold that loads the live
    deployed HTTPS URL inside a native Android shell, with build/publish
    instructions — produces a real installable APK / Play Store bundle
    (requires Node + Android Studio locally to build).

## [1.1.0]

### Changed
- Rebranded from MedTrack to **MediCal**: new logo, brand blue (`#155DFD`,
  sampled from the logo) replacing the previous teal across the UI.
- Added full **dark mode** (sidebar toggle + Settings), persisted per-user.

### Added
- **Visit cost tracking**: cash/insurance toggle per visit, itemized line
  items by category (reception, pharmacy, laboratory, x-ray, consultation,
  procedure, other).
- **Dashboard spending analytics**: year-to-date cash vs. insurance totals
  with a breakdown bar, plus a category breakdown on the new Reports page.
- **Refill tracking**: quantity remaining + low-stock threshold per
  medicine, quick +/- adjusters, a dashboard low-stock widget, and a
  low-stock search filter.
- **Export**: medication history, visit history, and yearly spending as
  CSV or a branded PDF from a new Reports page.
- **OCR auto-fill**: scanning an uploaded prescription photo (Tesseract)
  suggests doctor name, hospital name, and dose for review — never
  auto-saved without confirmation.
- Optional per-medicine **cost, payment method, and insurance-covered**
  flag.
- **Vaccination records** as their own type — dose number, next-due
  tracking, certificate upload.
- **Vitals on visits** — blood pressure, weight, heart rate per visit, with
  the latest reading surfaced on the dashboard.
- **Lab Tests & Imaging** — tracker for tests requested by physicians
  (CBC, X-Ray, etc.), with completion status and result file uploads.
- App **version** shown in the sidebar, with a GitHub Releases–based
  "Update available" check (configured via `GITHUB_REPO` in `.env`).

## [1.0.0]

Initial release.

### Added
- Admin login; admin creates further user logins.
- Doctor visits: doctor, hospital, visit date, optional prescription photo
  upload/capture.
- Medicines per visit: name, **composition** and **dose** mandatory (so
  alternates with the same composition can be found later), frequency,
  timing, manufacturer, start/end dates, symptom tags, photo upload.
- Dashboard: total medicines, active count, hospital visits, distinct
  doctors/hospitals, last visit date, next visit date, next medicine to take,
  medicines ending soon.
- Search by name, composition, manufacturer, doctor, hospital, symptom tag,
  status, and visit date range, plus "find alternates by composition."
- Retractable sidebar (collapses to icon-only, state persisted).
- Docker Compose deployment: PostgreSQL + FastAPI backend + Nginx-served
  static frontend.
