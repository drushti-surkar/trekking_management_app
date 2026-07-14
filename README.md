# Manzil - Trekking Management Application

MAD-II project by 23f2001500. Manzil - A role-based web app to manage trekking activities for **Admin**, **Trek Staff**, and **Trekkers (Users)**.

## Tech Stack
- **Backend:** Flask + Flask-SQLAlchemy
- **Auth:** Flask-Security-Too (token-based)
- **Frontend:** VueJS (CDN) + Bootstrap
- **Database:** SQLite
- **Caching:** Redis
- **Batch jobs:** Celery + Redis
- **Email (local):** Mailhog SMTP

## Project Structure
```
frontend/          Vue (CDN) SPA
  index.html       single Jinja2 entry point
  components/       Vue page components (.js)
  src/             store, router, app bootstrap
  img/             login-page photos (hero1..hero4.jpg)
backend/           Flask API
  app.py           app factory (serves ../frontend)
  models/          SQLAlchemy models
  routes/          API blueprints (auth, admin, staff, trekker)
  tasks.py, celery_app.py, cache.py, emailer.py, ...
  create_admin.py  seeds DB + admin
  requirements.txt
```

## Setup
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
python backend/app.py              # auto-creates DB + admin, runs on http://localhost:5001
```
On first run `app.py` programmatically creates the tables, roles, and the admin
(idempotent — existing data is never overwritten). To seed without starting the
server, run `python backend/create_admin.py` instead.

Default admin: `admin@manzil.com` / `admin123`

### Background jobs (Celery + Redis)
Requires Redis running (`redis-server`) and, for email, Mailhog (`localhost:1025`).
```bash
# in separate terminals (venv activated), from the backend/ directory:
cd backend
celery -A celery_app.celery worker --loglevel=info   # background worker
celery -A celery_app.celery beat   --loglevel=info   # scheduled jobs (daily/monthly)
```
Jobs: daily trek reminders, monthly activity report (HTML email to admin),
and user-triggered CSV export of trekking history (from the trekker dashboard).

## Data Model
- **User** — unified model, role = admin / staff / trekker
- **StaffProfile** — one-to-one staff details
- **Trek** — name, location, difficulty, duration, slots, assigned staff, status, dates
- **Booking** — user ↔ trek, status (Booked / Cancelled / Completed), payment status

Relationships: Staff↔Trek, Trek↔Booking, User↔Booking.

