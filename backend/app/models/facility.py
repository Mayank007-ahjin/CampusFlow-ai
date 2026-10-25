from sqlalchemy import Column, Integer, String, Float, DateTime, Enum as SQLEnum, Boolean
from sqlalchemy.sql import func
from datetime import datetime
import enum
from ..core.database import Base


class FacilityType(str, enum.Enum):
    """Types of campus facilities."""
    LIBRARY = "library"
    CANTEEN = "canteen"
    STATIONERY = "stationery"


class CrowdLevel(str, enum.Enum):
    """Crowd level classifications."""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"


class DataSource(str, enum.Enum):
    """Data source types."""
    MANUAL = "manual"
    STUDENT_REPORT = "student_report"
    SIMULATED = "simulated"
    SENSOR = "sensor"


class Facility(Base):
    """Campus facility model."""
    __tablename__ = "facilities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    type = Column(SQLEnum(FacilityType), nullable=False)
    location = Column(String(200))
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    # Operating hours
    opening_time = Column(String(5))  # Format: "08:00"
    closing_time = Column(String(5))  # Format: "22:00"
    is_open = Column(Boolean, default=True)

    # Capacity information
    total_capacity = Column(Integer, nullable=True)

    # Current status
    current_crowd_level = Column(SQLEnum(CrowdLevel), default=CrowdLevel.LOW)
    estimated_wait_minutes = Column(Integer, nullable=True)
    available_seats = Column(Integer, nullable=True)

    # Metadata
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    data_source = Column(SQLEnum(DataSource), default=DataSource.MANUAL)
    confidence_score = Column(Float, nullable=True)  # 0.0 to 1.0

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<Facility {self.name} ({self.type})>"


class Report(Base):
    """Student-submitted facility reports."""
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    facility_id = Column(Integer, nullable=False, index=True)

    # Report data
    crowd_level = Column(SQLEnum(CrowdLevel), nullable=True)
    estimated_wait_minutes = Column(Integer, nullable=True)
    available_seats = Column(Integer, nullable=True)
    queue_length = Column(Integer, nullable=True)

    # Additional context
    notes = Column(String(500), nullable=True)

    # Metadata
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    session_id = Column(String(64), nullable=True)  # Anonymous identifier
    is_validated = Column(Boolean, default=False)
    data_source = Column(SQLEnum(DataSource), default=DataSource.STUDENT_REPORT)

    def __repr__(self):
        return f"<Report facility_id={self.facility_id} at {self.timestamp}>"
