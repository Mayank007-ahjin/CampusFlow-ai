"""
Seed data script to populate initial facilities and sample reports.
Run this after creating the database to add demo data.
"""

from datetime import datetime, timedelta
import random

from app.core.database import SessionLocal, engine, Base
from app.models import Facility, Report, FacilityType, CrowdLevel, DataSource


def create_initial_facilities(db):
    """Create core facilities including new additions."""
    facilities = [
        Facility(
            name="Central Library(AB1 Branch)",
            type=FacilityType.LIBRARY,
            location="Building Academic Block 1, 3rd floor",
            latitude=28.472353,
            longitude=77.489328,
            opening_time="08:30 AM",
            closing_time="5:00 PM",
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
            location="Mess Building, Ground Floor",
            latitude=28.472839,
            longitude=77.489215,
            opening_time="07:30 AM",
            closing_time="10:00 PM",
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
            location="Near the Workshop Building",
            latitude=28.472416,
            longitude=77.489444,
            opening_time="08:30 AM",
            closing_time="06:00 PM",
            is_open=True,
            total_capacity=None,
            current_crowd_level=CrowdLevel.MODERATE,
            estimated_wait_minutes=4,
            available_seats=None,
            data_source=DataSource.SIMULATED,
            confidence_score=0.5,
        ),
        Facility(
            name="Central Library (AB2 Branch)",
            type=FacilityType.LIBRARY,
            location="Academic Block 2, Ground Floor",
            latitude=28.6150,
            longitude=77.2100,
            opening_time="08:00 AM",
            closing_time="08:00 PM",
            is_open=True,
            total_capacity=150,
            current_crowd_level=CrowdLevel.MODERATE,
            available_seats=68,
            estimated_wait_minutes=None,
            data_source=DataSource.SIMULATED,
            confidence_score=0.8,
        ),
        # Facility(
        #     name="College Administrative Office",
        #     type=FacilityType.OFFICE,
        #     location="Adjacent to Academic Block 1",
        #     latitude=28.472664,
        #     longitude=77.488672,
        #     opening_time="10:00 AM",
        #     closing_time="05:00 PM",
        #     is_open=True,
        #     total_capacity=50,
        #     current_crowd_level=CrowdLevel.LOW,
        #     estimated_wait_minutes=5,
        #     available_seats=15,
        #     data_source=DataSource.SIMULATED,
        #     confidence_score=0.75,
        # ),
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

    for facility in facilities:
        for i in range(5):
            timestamp = now - timedelta(minutes=random.randint(5, 120))
            reports.append(Report(
                facility_id=facility.id,
                crowd_level=random.choice([CrowdLevel.LOW, CrowdLevel.MODERATE]),
                available_seats=random.randint(20, 50) if facility.type == FacilityType.LIBRARY else None,
                estimated_wait_minutes=random.randint(2, 10) if facility.type != FacilityType.LIBRARY else None,
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
        # Clear existing data to allow fresh seed with 12-hr clock and new facilities
        db.query(Report).delete()
        db.query(Facility).delete()
        db.commit()
        print("[OK] Cleared existing database records")

        # Create facilities
        facilities = create_initial_facilities(db)

        # Create sample reports
        create_sample_reports(db, facilities)

        print("\n[SUCCESS] Database seeding completed successfully!")
        print("\nCreated facilities:")
        for f in facilities:
            print(f"  - {f.name} ({f.type.value}) | {f.opening_time} - {f.closing_time}")

    except Exception as e:
        print(f"\n[ERROR] Error during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
