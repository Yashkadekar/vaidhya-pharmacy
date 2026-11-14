import os
from dotenv import load_dotenv
load_dotenv()
from app.database import Base, engine, SessionLocal
from app.models import User
from app.security import hash_password

Base.metadata.create_all(bind=engine)
email = os.getenv("ADMIN_EMAIL")
password = os.getenv("ADMIN_PASSWORD")
if not email or not password or password.startswith("ChangeThis"):
    raise SystemExit("Set ADMIN_EMAIL and a strong ADMIN_PASSWORD in .env before running this script.")
db = SessionLocal()
try:
    existing = db.query(User).filter(User.email == email.lower()).first()
    if existing:
        existing.role = "admin"
        existing.password_hash = hash_password(password)
    else:
        db.add(User(name="Vaidhya Admin", email=email.lower(), password_hash=hash_password(password), role="admin"))
    db.commit()
    print(f"Admin account ready: {email}. Keep the credentials private.")
finally:
    db.close()
