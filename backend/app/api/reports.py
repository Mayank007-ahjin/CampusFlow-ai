from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta

from ..core.database import get_db
from ..models import schemas, Report, Facility
from ..services.crowd_estimator import CrowdEstimatorService

router = APIRouter()


@router.post("/reports", response_model=schemas.ReportResponse, status_code=status.HTTP_201_CREATED)
async def create_report(
    report: schemas.ReportCreate,
    db: Session = Depends(get_db)
):
    """
    Submit a student report about facility conditions.

    - **report**: Report data including crowd level, wait time, or seat availability
    """
    # Validate facility exists
    facility = db.query(Facility).filter(Facility.id == report.facility_id).first()
    if not facility:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Facility with id {report.facility_id} not found"
        )

    # Validate at least one data field is provided
    if not any([
        report.crowd_level,
        report.estimated_wait_minutes is not None,
        report.available_seats is not None,
        report.queue_length is not None
    ]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one data field (crowd_level, wait time, seats, or queue) must be provided"
        )

    # Create report
    db_report = Report(**report.model_dump())
    db.add(db_report)
    db.commit()
    db.refresh(db_report)

    # Update facility estimate based on new report
    estimator = CrowdEstimatorService(db)
    estimator.update_facility_from_reports(report.facility_id)

    return db_report


@router.get("/reports", response_model=schemas.ReportListResponse)
async def get_reports(
    facility_id: Optional[int] = None,
    hours: int = 24,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get recent facility reports.

    - **facility_id**: Filter by facility (optional)
    - **hours**: Get reports from last N hours (default: 24)
    - **limit**: Maximum number of reports to return (default: 100)
    """
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)

    query = db.query(Report).filter(Report.timestamp >= cutoff_time)

    if facility_id:
        query = query.filter(Report.facility_id == facility_id)

    reports = query.order_by(Report.timestamp.desc()).limit(limit).all()

    return {
        "reports": reports,
        "count": len(reports)
    }


@router.get("/reports/{report_id}", response_model=schemas.ReportResponse)
async def get_report(
    report_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific report by ID.

    - **report_id**: The ID of the report
    """
    report = db.query(Report).filter(Report.id == report_id).first()

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report with id {report_id} not found"
        )

    return report
