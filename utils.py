"""Shared helpers."""


def recalc_available_slots(trek):
    """Keep available_slots = total_slots - active(Booked) bookings."""
    booked = sum(1 for b in trek.bookings if b.status == "Booked")
    trek.available_slots = max(trek.total_slots - booked, 0)
    return trek.available_slots
