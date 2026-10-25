from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
import statistics

from ..models import Facility, Report, CrowdLevel, DataSource
from ..models.schemas import EstimateResponse
from ..core.config import settings


class CrowdEstimatorService:
    """Service for estimating crowd levels and wait times based on reports."""

    def __init__(self, db: Session):
        self.db = db
        self.staleness_threshold = timedelta(
            minutes=settings.REPORT_STALENESS_THRESHOLD_MINUTES
        )

    def get_facility_estimate(self, facility_id: int) -> EstimateResponse:
        """
        Get current crowd estimate for a facility.

        Uses recent reports to calculate estimates with confidence scoring.
        Falls back to simulated data if no recent reports exist.
        """
        facility = self.db.query(Facility).filter(Facility.id == facility_id).first()

        if not facility:
            raise ValueError(f"Facility {facility_id} not found")

        # Get recent reports
        cutoff_time = datetime.utcnow() - timedelta(minutes=30)
        recent_reports = (
            self.db.query(Report)
            .filter(Report.facility_id == facility_id)
            .filter(Report.timestamp >= cutoff_time)
            .order_by(Report.timestamp.desc())
            .limit(10)
            .all()
        )

        # Check staleness
        is_stale = (
            not facility.last_updated or
            datetime.utcnow() - facility.last_updated > self.staleness_threshold
        )

        return EstimateResponse(
            facility_id=facility.id,
            facility_name=facility.name,
            crowd_level=facility.current_crowd_level,
            estimated_wait_minutes=facility.estimated_wait_minutes,
            available_seats=facility.available_seats,
            confidence_score=facility.confidence_score,
            last_updated=facility.last_updated or datetime.utcnow(),
            data_source=facility.data_source,
            staleness_warning=is_stale
        )

    def update_facility_from_reports(self, facility_id: int) -> None:
        """
        Update facility status based on recent reports.

        Aggregates multiple reports using weighted averaging based on recency.
        """
        facility = self.db.query(Facility).filter(Facility.id == facility_id).first()

        if not facility:
            return

        # Get reports from last 30 minutes
        cutoff_time = datetime.utcnow() - timedelta(minutes=30)
        recent_reports = (
            self.db.query(Report)
            .filter(Report.facility_id == facility_id)
            .filter(Report.timestamp >= cutoff_time)
            .order_by(Report.timestamp.desc())
            .all()
        )

        if not recent_reports:
            return

        # Aggregate crowd levels
        crowd_levels = [r.crowd_level for r in recent_reports if r.crowd_level]
        if crowd_levels:
            facility.current_crowd_level = self._aggregate_crowd_level(crowd_levels)

        # Aggregate wait times
        wait_times = [r.estimated_wait_minutes for r in recent_reports if r.estimated_wait_minutes is not None]
        if wait_times:
            facility.estimated_wait_minutes = self._weighted_average(
                wait_times,
                [self._time_weight(r.timestamp) for r in recent_reports if r.estimated_wait_minutes is not None]
            )

        # Aggregate seat availability
        seat_counts = [r.available_seats for r in recent_reports if r.available_seats is not None]
        if seat_counts:
            facility.available_seats = self._weighted_average(
                seat_counts,
                [self._time_weight(r.timestamp) for r in recent_reports if r.available_seats is not None]
            )

        # Calculate confidence score
        facility.confidence_score = self._calculate_confidence(recent_reports)
        facility.data_source = DataSource.STUDENT_REPORT
        facility.last_updated = datetime.utcnow()

        self.db.commit()

    def _aggregate_crowd_level(self, levels: list[CrowdLevel]) -> CrowdLevel:
        """Aggregate crowd levels by taking the most common recent value."""
        if not levels:
            return CrowdLevel.LOW

        # Weight recent reports more heavily
        level_scores = {
            CrowdLevel.LOW: 0,
            CrowdLevel.MODERATE: 1,
            CrowdLevel.HIGH: 2
        }

        # Convert to numeric, take weighted average, convert back
        numeric_levels = [level_scores[level] for level in levels]
        avg_score = statistics.mean(numeric_levels)

        if avg_score < 0.67:
            return CrowdLevel.LOW
        elif avg_score < 1.67:
            return CrowdLevel.MODERATE
        else:
            return CrowdLevel.HIGH

    def _weighted_average(self, values: list[float], weights: list[float]) -> int:
        """Calculate weighted average and round to integer."""
        if not values or not weights:
            return 0

        total = sum(v * w for v, w in zip(values, weights))
        weight_sum = sum(weights)

        return round(total / weight_sum) if weight_sum > 0 else 0

    def _time_weight(self, timestamp: datetime) -> float:
        """
        Calculate weight based on report age.
        More recent reports get higher weights.
        """
        age_minutes = (datetime.utcnow() - timestamp).total_seconds() / 60

        # Exponential decay: weight = e^(-age/10)
        # Reports lose ~10% weight per minute
        import math
        return math.exp(-age_minutes / 10)

    def _calculate_confidence(self, reports: list[Report]) -> float:
        """
        Calculate confidence score based on report count and consistency.

        Returns a value between 0.0 and 1.0.
        """
        if not reports:
            return 0.0

        # More reports = higher confidence
        count_score = min(len(reports) / 5.0, 1.0)  # Max at 5 reports

        # Recent reports = higher confidence
        avg_age_minutes = statistics.mean([
            (datetime.utcnow() - r.timestamp).total_seconds() / 60
            for r in reports
        ])
        recency_score = max(0.0, 1.0 - (avg_age_minutes / 30.0))  # Decay over 30 min

        # Combine scores
        return (count_score * 0.6 + recency_score * 0.4)
