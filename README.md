# Trekking Management Application (TMA) — V2

MAD-II project (23f2001500). A role-based web app to manage trekking activities for **Admin**, **Trek Staff**, and **Trekkers (Users)**.

## Tech Stack
- **Backend:** Flask + Flask-SQLAlchemy
- **Auth:** Flask-Security-Too (token-based)
- **Frontend:** VueJS (CDN) + Bootstrap
- **Database:** SQLite
- **Caching:** Redis
- **Batch jobs:** Celery + Redis
- **Email (local):** Mailhog SMTP

## Setup
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python create_admin.py     # creates DB, seeds roles + Admin
python app.py              # runs on http://localhost:5000
```

Default admin: `admin@tma.com` / `admin123`

## Data Model
- **User** — unified model, role = admin / staff / trekker
- **StaffProfile** — one-to-one staff details
- **Trek** — name, location, difficulty, duration, slots, assigned staff, status, dates
- **Booking** — user ↔ trek, status (Booked / Cancelled / Completed), payment status

Relationships: Staff↔Trek, Trek↔Booking, User↔Booking.

## Milestone Progress
- [x] M0 — GitHub setup
- [x] M1 — Database models & schema
- [x] M2 — Authentication & role-based access
- [x] M3 — Admin dashboard
- [x] M4 — Trek staff dashboard
- [x] M5 — User dashboard & booking
- [ ] M6 — Booking history & status tracking
- [ ] M7 — Celery jobs (reminders, reports, CSV export)
- [ ] M8 — Redis caching
