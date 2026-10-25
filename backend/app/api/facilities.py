from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from ..core.database import get_db
from ..models import schemas, Facility, FacilityType
from ..services.crowd_estimator import CrowdEstimatorService

router = APIRouter()


@router.get("/facilities", response_model=schemas.FacilityListResponse)
async def get_facilities(
    facility_type: Optional[FacilityType] = None,
    include_closed: bool = False,
    db: Session = Depends(get_db)
):
    """
    Get all facilities with current status.

    - **facility_type**: Filter by facility type (optional)
    - **include_closed**: Include currently closed facilities (default: False)
    """
    query = db.query(Facility)

    if facility_type:
        query = query.filter(Facility.type == facility_type)

    if not include_closed:
        query = query.filter(Facility.is_open == True)

    facilities = query.all()

    return {
        "facilities": facilities,
        "count": len(facilities)
    }


@router.get("/facilities/{facility_id}", response_model=schemas.FacilityResponse)
async def get_facility(
    facility_id: int,
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific facility.

    - **facility_id**: The ID of the facility
    """
    facility = db.query(Facility).filter(Facility.id == facility_id).first()

    if not facility:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Facility with id {facility_id} not found"
        )

    return facility


@router.post("/facilities", response_model=schemas.FacilityResponse, status_code=status.HTTP_201_CREATED)
async def create_facility(
    facility: schemas.FacilityCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new facility (admin endpoint).

    - **facility**: Facility details
    """
    db_facility = Facility(**facility.model_dump())
    db.add(db_facility)
    db.commit()
    db.refresh(db_facility)

    return db_facility


@router.patch("/facilities/{facility_id}", response_model=schemas.FacilityResponse)
async def update_facility(
    facility_id: int,
    facility_update: schemas.FacilityUpdate,
    db: Session = Depends(get_db)
):
    """
    Update facility information (admin endpoint).

    - **facility_id**: The ID of the facility
    - **facility_update**: Fields to update
    """
    db_facility = db.query(Facility).filter(Facility.id == facility_id).first()

    if not db_facility:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Facility with id {facility_id} not found"
        )

    # Update only provided fields
    update_data = facility_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_facility, field, value)

    db.commit()
    db.refresh(db_facility)

    return db_facility


@router.get("/facilities/{facility_id}/estimate", response_model=schemas.EstimateResponse)
async def get_facility_estimate(
    facility_id: int,
    db: Session = Depends(get_db)
):
    """
    Get current crowd estimate for a facility.

    - **facility_id**: The ID of the facility
    """
    facility = db.query(Facility).filter(Facility.id == facility_id).first()

    if not facility:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Facility with id {facility_id} not found"
        )

    # Use crowd estimator service to get current estimate
    estimator = CrowdEstimatorService(db)
    estimate = estimator.get_facility_estimate(facility_id)

    return estimate
