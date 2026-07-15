from collections import defaultdict
from datetime import date

from flask import Blueprint, jsonify

from models import Trek, Booking

public_bp = Blueprint("public", __name__, url_prefix="/api/public")


def _last_six_months():
    today = date.today()
    months = []
    y, m = today.year, today.month
    for i in range(5, -1, -1):
        mm, yy = m - i, y
        while mm <= 0:
            mm += 12
            yy -= 1
        months.append((yy, mm))
    return months


MONTH_ABBR = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


@public_bp.get("/stats")
def stats():
    treks = Trek.query.all()
    bookings = Booking.query.all()

    active = [b for b in bookings if b.status in ("Booked", "Completed")]

    totals = {
        "treks": len(treks),
        "open_treks": sum(1 for t in treks if t.status == "Open"),
        "completed_treks": sum(1 for t in treks if t.status == "Completed"),
        "participants": len(active),
    }

    popular = []
    for t in treks:
        count = sum(1 for b in t.bookings if b.status in ("Booked", "Completed"))
        if count:
            popular.append({"name": t.name, "bookings": count})
    popular.sort(key=lambda x: x["bookings"], reverse=True)
    popular = popular[:5]

    difficulty = {"Easy": 0, "Moderate": 0, "Hard": 0}
    for t in treks:
        if t.difficulty in difficulty:
            difficulty[t.difficulty] += 1

    bucket = defaultdict(int)
    for b in bookings:
        if b.booking_date:
            bucket[(b.booking_date.year, b.booking_date.month)] += 1
    months = _last_six_months()
    monthly_trend = {
        "labels": [MONTH_ABBR[mm] for (_, mm) in months],
        "counts": [bucket.get((yy, mm), 0) for (yy, mm) in months],
    }

    status_breakdown = {
        "Booked": sum(1 for b in bookings if b.status == "Booked"),
        "Completed": sum(1 for b in bookings if b.status == "Completed"),
        "Cancelled": sum(1 for b in bookings if b.status == "Cancelled"),
    }

    return jsonify(
        totals=totals,
        popular_treks=popular,
        difficulty=difficulty,
        monthly_trend=monthly_trend,
        status_breakdown=status_breakdown,
    )
