from app import app, seed_admin

if __name__ == "__main__":
    seed_admin()
    print(f"Admin ready -> {app.config['ADMIN_EMAIL']} / {app.config['ADMIN_PASSWORD']}")
