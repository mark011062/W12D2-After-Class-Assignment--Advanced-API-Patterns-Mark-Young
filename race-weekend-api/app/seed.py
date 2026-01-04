# app/seed.py
from datetime import date
from sqlalchemy import select

from app.core.security import hash_password
from app.db.database import Base, engine, SessionLocal
from app.db.models import User, Event, Task

def run_seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # admin
        admin_email = "admin@race.local"
        admin = db.execute(select(User).where(User.email == admin_email)).scalar_one_or_none()
        if not admin:
            admin = User(email=admin_email, password_hash=hash_password("AdminPass1!"), role="admin")
            db.add(admin)
            db.commit()
            db.refresh(admin)

        # user
        user_email = "rider@race.local"
        rider = db.execute(select(User).where(User.email == user_email)).scalar_one_or_none()
        if not rider:
            rider = User(email=user_email, password_hash=hash_password("RiderPass1!"), role="user")
            db.add(rider)
            db.commit()
            db.refresh(rider)

        # event
        event = db.execute(select(Event).where(Event.name == "NCM Weekend")).scalar_one_or_none()
        if not event:
            event = Event(
                name="NCM Weekend",
                track_name="NCM Motorsports Park",
                city="Bowling Green",
                state="KY",
                event_date=date(2026, 1, 10),
            )
            db.add(event)
            db.commit()
            db.refresh(event)

        # tasks (team-wide + assigned)
        existing = db.execute(select(Task).where(Task.event_id == event.id)).scalars().all()
        if not existing:
            tasks = [
                Task(event_id=event.id, title="Load bike into trailer", category="travel", priority=2, assignee_id=None),
                Task(event_id=event.id, title="Set tire pressures (cold)", category="pit", priority=1, assignee_id=rider.id),
                Task(event_id=event.id, title="Safety wire drain bolt", category="tech", priority=1, assignee_id=rider.id),
                Task(event_id=event.id, title="Pack spare levers + tools", category="prep", priority=2, assignee_id=None),
                Task(event_id=event.id, title="Check brake pad thickness", category="safety", priority=1, assignee_id=rider.id),
            ]
            db.add_all(tasks)
            db.commit()

        print("✅ Seed complete.")
        print("Admin login: admin@race.local / AdminPass1!")
        print("User login:  rider@race.local / RiderPass1!")

    finally:
        db.close()

if __name__ == "__main__":
    run_seed()
