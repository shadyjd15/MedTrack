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