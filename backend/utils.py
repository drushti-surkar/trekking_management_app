from models import Booking


def recalc_available_slots(trek):
    booked = Booking.query.filter_by(trek_id=trek.id, status="Booked").count()
    trek.available_slots = max(trek.total_slots - booked, 0)
    return trek.available_slots


def complete_trek_bookings(trek):
    """When a trek is marked Completed, roll its active bookings to Completed
    so each trekker's history reflects the finished trek."""
    for b in trek.bookings:
        if b.status == "Booked":
            b.status = "Completed"
