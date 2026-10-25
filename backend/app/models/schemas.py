from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class FacilityType(str, Enum):
    """Types of campus facilities."""
    LIBRARY = "library"
    CANTEEN = "canteen"
    STATIONERY = "stationery"


class CrowdLevel(str, Enum):
    """Crowd level classifications."""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"


class DataSource(str, Enum):
    """Data source types."""
    MANUAL = "manual"
    STUDENT_REPORT = "student_report"
    SIMULATED = "simulated"
    SENSOR = "sensor"


# ===== Facility Schemas =====

class FacilityBase(BaseModel):
    """Base facility schema."""
    name: str = Field(..., max_length=100)
    type: FacilityType
    location: Optional[str] = Field(None, max_length=200)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    opening_time: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$")
    closing_time: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$")
    total_capacity: Optional[int] = Field(None, ge=0)


class FacilityCreate(FacilityBase):
    """Schema for creating a facility."""
    pass


class FacilityUpdate(BaseModel):
    """Schema for updating a facility."""
    name: Optional[str] = Field(None, max_length=100)
    location: Optional[str] = Field(None, max_length=200)
    opening_time: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$")
    closing_time: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$")
    is_open: Optional[bool] = None
    total_capacity: Optional[int] = Field(None, ge=0)


class FacilityResponse(FacilityBase):
    """Schema for facility response."""
    id: int
    is_open: bool
    current_crowd_level: CrowdLevel
    estimated_wait_minutes: Optional[int]
    available_seats: Optional[int]
    last_updated: datetime
    data_source: DataSource
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    created_at: datetime

    class Config:
        from_attributes = True


class FacilityListResponse(BaseModel):
    """Schema for list of facilities."""
    facilities: List[FacilityResponse]
    count: int


# ===== Report Schemas =====

class ReportCreate(BaseModel):
    """Schema for creating a report."""
    facility_id: int = Field(..., gt=0)
    crowd_level: Optional[CrowdLevel] = None
    estimated_wait_minutes: Optional[int] = Field(None, ge=0, le=300)
    available_seats: Optional[int] = Field(None, ge=0)
    queue_length: Optional[int] = Field(None, ge=0)
    notes: Optional[str] = Field(None, max_length=500)

    @field_validator('crowd_level', 'estimated_wait_minutes', 'available_seats', 'queue_length')
    @classmethod
    def at_least_one_field(cls, v, info):
        """Ensure at least one data field is provided."""
        return v


class ReportResponse(BaseModel):
    """Schema for report response."""
    id: int
    facility_id: int
    crowd_level: Optional[CrowdLevel]
    estimated_wait_minutes: Optional[int]
    available_seats: Optional[int]
    queue_length: Optional[int]
    notes: Optional[str]
    timestamp: datetime
    is_validated: bool
    data_source: DataSource

    class Config:
        from_attributes = True


class ReportListResponse(BaseModel):
    """Schema for list of reports."""
    reports: List[ReportResponse]
    count: int


# ===== Estimate Schemas =====

class EstimateResponse(BaseModel):
    """Schema for facility estimate."""
    facility_id: int
    facility_name: str
    crowd_level: CrowdLevel
    estimated_wait_minutes: Optional[int]
    available_seats: Optional[int]
    confidence_score: Optional[float]
    last_updated: datetime
    data_source: DataSource
    staleness_warning: bool = False


# ===== Recommendation Schemas =====

class RecommendationRequest(BaseModel):
    """Schema for recommendation request."""
    query: str = Field(..., min_length=1, max_length=500)
    facility_types: Optional[List[FacilityType]] = None
    max_wait_minutes: Optional[int] = Field(None, ge=0)
    include_closed: bool = False


class RecommendationOption(BaseModel):
    """Schema for a single recommendation option."""
    facility_id: int
    facility_name: str
    facility_type: FacilityType
    crowd_level: CrowdLevel
    estimated_wait_minutes: Optional[int]
    available_seats: Optional[int]
    distance_meters: Optional[float] = None
    score: float = Field(..., ge=0.0, le=1.0)
    reason: str


class RecommendationResponse(BaseModel):
    """Schema for recommendation response."""
    query: str
    answer: str
    recommendations: List[RecommendationOption]
    timestamp: datetime


# ===== Proactive Alert Schemas =====

class AlertResponse(BaseModel):
    """Schema for proactive peak-hour alert."""
    id: int
    facility_name: str
    alert_type: str
    severity: str
    message: str
    timestamp: datetime


class AlertListResponse(BaseModel):
    """Schema for list of alerts."""
    alerts: List[AlertResponse]
    count: int


# ===== Error Schemas =====

class ErrorResponse(BaseModel):
    """Schema for error responses."""
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ===== Health Check =====

class HealthResponse(BaseModel):
    """Schema for health check response."""
    status: str
    timestamp: datetime
    version: str
