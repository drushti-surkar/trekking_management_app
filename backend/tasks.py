import csv
import os
import time
from datetime import date, timedelta

from flask import current_app

from celery_app import celery
from extensions import db  # noqa: F401  (kept for parity / future writes)
from models import User, Trek, Booking, Role
from emailer import send_email


@celery.task(name="tasks.daily_trek_reminders")
def daily_trek_reminders():
    today = date.today()
    window_end = today + timedelta(days=2)
    treks = Trek.query.filter(
        Trek.status == "Open",
        Trek.start_date.isnot(None),
        Trek.start_date >= today,
        Trek.start_date <= window_end,
    ).all()

    emails_sent = 0
    for trek in treks:
        for b in trek.bookings:
            if b.status == "Booked" and b.user:
                html = (
                    f"<h3>Trek Reminder</h3>"
                    f"<p>Hi {b.user.name}, your trek <strong>{trek.name}</strong> "
                    f"({trek.location}) starts on <strong>{trek.start_date}</strong>.</p>"
                    f"<p>Difficulty: {trek.difficulty} · Duration: {trek.duration_days} days.</p>"
                    f"<p>Get ready and pack well!</p>"
                )
                send_email(b.user.email, f"Reminder: {trek.name} starts soon", html)
                emails_sent += 1

    return {"treks": len(treks), "emails_sent": emails_sent}


@celery.task(name="tasks.monthly_activity_report")
def monthly_activity_report():
    today = date.today()
    first_this_month = today.replace(day=1)
    last_month_end = first_this_month - timedelta(days=1)
    first_last_month = last_month_end.replace(day=1)

    # Treks that ran last month (by start date)
    treks_conducted = Trek.query.filter(
        Trek.start_date.isnot(None),
        Trek.start_date >= first_last_month,
        Trek.start_date <= last_month_end,
    ).count()

    # Participants (bookings placed last month, still active/completed)
    participants = Booking.query.filter(
        Booking.booking_date >= first_last_month,
        Booking.booking_date <= last_month_end + timedelta(days=1),
        Booking.status.in_(["Booked", "Completed"]),
    ).count()

    popular = []
    for trek in Trek.query.all():
        count = sum(1 for b in trek.bookings if b.status in ("Booked", "Completed"))
        if count:
            popular.append((trek.name, count))
    popular.sort(key=lambda x: x[1], reverse=True)
    popular = popular[:5]

    rows = "".join(f"<tr><td>{n}</td><td>{c}</td></tr>" for n, c in popular) or \
        "<tr><td colspan='2'>No bookings yet</td></tr>"
    html = f"""
    <h2>Trekking Activity Report</h2>
    <p>Period: {first_last_month} to {last_month_end}</p>
    <ul>
      <li><strong>Treks conducted:</strong> {treks_conducted}</li>
      <li><strong>Participants:</strong> {participants}</li>
    </ul>
    <h3>Most Popular Treks</h3>
    <table border="1" cellpadding="6" cellspacing="0">
      <tr><th>Trek</th><th>Bookings</th></tr>
      {rows}
    </table>
    """

    admin_email = current_app.config.get("ADMIN_EMAIL")
    send_email(admin_email, "Monthly Trekking Activity Report", html)
    return {
        "treks_conducted": treks_conducted,
        "participants": participants,
        "popular": popular,
    }


@celery.task(name="tasks.export_bookings_csv")
def export_bookings_csv(user_id):
    user = User.query.get(user_id)
    if not user:
        return {"error": "user not found"}

    export_dir = current_app.config["EXPORT_DIR"]
    os.makedirs(export_dir, exist_ok=True)
    fname = f"booking_history_{user_id}_{int(time.time())}.csv"
    path = os.path.join(export_dir, fname)

    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Booking ID", "Trek", "Location", "Difficulty",
            "Booking Date", "Trek Status", "Booking Status", "Payment",
        ])
        for b in sorted(user.bookings, key=lambda x: x.id):
            t = b.trek
            writer.writerow([
                b.id,
                t.name if t else "",
                t.location if t else "",
                t.difficulty if t else "",
                b.booking_date.strftime("%Y-%m-%d") if b.booking_date else "",
                t.status if t else "",
                b.status,
                b.payment_status,
            ])

    html = (
        f"<p>Hi {user.name}, your trekking history export "
        f"({len(user.bookings)} records) is ready. "
        f"Download it from your dashboard.</p>"
    )
    send_email(user.email, "Your trekking history export is ready", html, attachment_path=path)

    return {"file": fname, "records": len(user.bookings)}
