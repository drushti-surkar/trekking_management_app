"""Optional: seed the database + admin from the command line.

Running `python app.py` already does this automatically on startup; this
script is kept for convenience / explicit seeding.
(Manual DB creation via DB Browser etc. is NOT allowed by the spec.)
"""
from app import app, seed_admin

if __name__ == "__main__":
    seed_admin()
    print(f"Admin ready -> {app.config['ADMIN_EMAIL']} / {app.config['ADMIN_PASSWORD']}")
