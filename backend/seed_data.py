"""
Seed data script to populate initial facilities and sample reports.
Run this after creating the database to add demo data.
"""

from datetime import datetime, timedelta
import random

from app.core.database import SessionLocal, engine, Base
from app.models import Facility, Report, FacilityType, CrowdLevel, DataSource


def create_initial_facilities(db):
    """Create the three core facilities."""
    facilities = [
        Facility(
            name="Central Library",
            type=FacilityType.LIBRARY,
            location="Building AB2, Ground Floor",
            latitude=28.6139,
            longitude=77.2090,
            opening_time="08:30",
            closing_time="22:00",
            is_open=True,
            total_capacity=120,
            current_crowd_level=CrowdLevel.LOW,
            available_seats=42,
            estimated_wait_minutes=None,
            data_source=DataSource.SIMULATED,
            confidence_score=0.7,
        ),
        Facility(
            name="Main Canteen",
            type=FacilityType.CANTEEN,
            location="MESS building, ground Floor",
            latitude=28.6145,
            longitude=77.2095,
            opening_time="07:30",
            closing_time="21:00",
            is_open=True,
            total_capacity=200,
            current_crowd_level=CrowdLevel.HIGH,
            estimated_wait_minutes=10,
            available_seats=None,
            data_source=DataSource.SIMULATED,
            confidence_score=0.6,
        ),
        Facility(
            name="Stationery & Print Shop",
            type=FacilityType.STATIONERY,
            location="Near the Worshop building",
            latitude=28.6142,
            longitude=77.2088,
            opening_time="08:30",
            closing_time="18:00",
            is_open=True,
            total_capacity=None,
            current_crowd_level=CrowdLevel.MODERATE,
            estimated_wait_minutes=4,
            available_seats=None,
            data_source=DataSource.SIMULATED,
            confidence_score=0.5,
        ),
    ]

    for facility in facilities:
        db.add(facility)

    db.commit()
    print(f"[OK] Created {len(facilities)} facilities")
    return facilities


def create_sample_reports(db, facilities):
    """Create sample historical reports for demo purposes."""
    reports = []
    now = datetime.utcnow()

    # Library reports (last 2 hours)
    library = facilities[0]
    for i in range(8):
        timestamp = now - timedelta(minutes=random.randint(5, 120))
        reports.append(Report(
            facility_id=library.id,
            crowd_level=random.choice([CrowdLevel.LOW, CrowdLevel.LOW, CrowdLevel.MODERATE]),
            available_seats=random.randint(30, 60),
            timestamp=timestamp,
            data_source=DataSource.STUDENT_REPORT,
        ))

    # Canteen reports (last 2 hours)
    canteen = facilities[1]
    for i in range(10):
        timestamp = now - timedelta(minutes=random.randint(5, 120))
        crowd = random.choice([CrowdLevel.MODERATE, CrowdLevel.HIGH, CrowdLevel.HIGH])
        wait = random.randint(10, 25) if crowd == CrowdLevel.HIGH else random.randint(5, 12)
        reports.append(Report(
            facility_id=canteen.id,
            crowd_level=crowd,
            estimated_wait_minutes=wait,
            queue_length=random.randint(8, 20),
            timestamp=timestamp,
            data_source=DataSource.STUDENT_REPORT,
        ))

    # Stationery reports (last 2 hours)
    stationery = facilities[2]
    for i in range(6):
        timestamp = now - timedelta(minutes=random.randint(5, 120))
        reports.append(Report(
            facility_id=stationery.id,
            crowd_level=random.choice([CrowdLevel.LOW, CrowdLevel.MODERATE]),
            estimated_wait_minutes=random.randint(2, 8),
            queue_length=random.randint(1, 5),
            timestamp=timestamp,
            data_source=DataSource.STUDENT_REPORT,
        ))

    for report in reports:
        db.add(report)

    db.commit()
    print(f"[OK] Created {len(reports)} sample reports")


def seed_database():
    """Main seeding function."""
    print("Starting database seeding...")

    # Create tables
    Base.metadata.create_all(bind=engine)
    print("[OK] Database tables created")

    # Create session
    db = SessionLocal()

    try:
        # Check if data already exists
        existing_facilities = db.query(Facility).count()
        if existing_facilities > 0:
            print(f"[WARNING] Database already has {existing_facilities} facilities. Skipping seed.")
            return

        # Create facilities
        facilities = create_initial_facilities(db)

        # Create sample reports
        create_sample_reports(db, facilities)

        print("\n[SUCCESS] Database seeding completed successfully!")
        print("\nCreated facilities:")
        for f in facilities:
            print(f"  - {f.name} ({f.type.value})")

    except Exception as e:
        print(f"\n[ERROR] Error during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
