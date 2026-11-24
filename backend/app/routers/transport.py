from typing import List, Optional
from datetime import datetime, timezone
import re
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import get_db
from app.models.user import User, UserRole, AggregatorProfile
from app.models.transport import TransportJob, TransportStatus
from app.models.order import Order, OrderStatus, OrderItem
from app.schemas.transport import (
    TransportJobResponse,
    TransportStatusUpdate,
    TransportRejectRequest,
    TransportPickupRequest,
    TransportDeliverRequest,
    AggregatorStatsResponse,
    AggregatorProfileResponse,
    AggregatorProfileUpdate
)
from app.routers.deps import get_current_user, require_role

router = APIRouter(prefix="/transport", tags=["Logistics & Transport Jobs"])


@router.get("/stats", response_model=AggregatorStatsResponse)
def get_aggregator_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.AGGREGATOR))
):
    """
    Dashboard KPI Counts based strictly on jobs assigned to the authenticated aggregator.
    """
    jobs = db.query(TransportJob).filter(TransportJob.aggregator_id == current_user.id).all()
    
    total_assigned = len(jobs)
    pending_pickups = len([j for j in jobs if j.status in (TransportStatus.ACCEPTED, TransportStatus.ASSIGNED)])
    pending_deliveries = len([j for j in jobs if j.status in (TransportStatus.PICKED_UP, TransportStatus.IN_TRANSIT)])
    completed_trips = len([j for j in jobs if j.status in (TransportStatus.DELIVERED, TransportStatus.COMPLETED)])
    
    return AggregatorStatsResponse(
        total_assigned=total_assigned,
        pending_pickups=pending_pickups,
        pending_deliveries=pending_deliveries,
        completed_trips=completed_trips
    )


@router.get("/jobs", response_model=List[TransportJobResponse])
def get_transport_jobs(
    status_filter: Optional[str] = Query(None, alias="status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lists transport assignments for the authenticated aggregator or admin.
    Aggregators only see jobs assigned to their own accounts.
    """
    query = db.query(TransportJob)
    if current_user.role == UserRole.AGGREGATOR:
        query = query.filter(TransportJob.aggregator_id == current_user.id)
    elif current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access transport jobs")

    if status_filter:
        if status_filter == "active":
            query = query.filter(TransportJob.status.in_([
                TransportStatus.ACCEPTED,
                TransportStatus.PICKED_UP,
                TransportStatus.PICKUP_IN_PROGRESS,
                TransportStatus.IN_TRANSIT,
                TransportStatus.DELIVERED
            ]))
        elif status_filter == "assigned":
            query = query.filter(TransportJob.status == TransportStatus.ASSIGNED)
        elif status_filter == "completed":
            query = query.filter(TransportJob.status.in_([TransportStatus.COMPLETED, TransportStatus.DELIVERED]))
        else:
            query = query.filter(TransportJob.status == status_filter)

    return query.order_by(desc(TransportJob.assigned_at)).all()


@router.get("/jobs/{job_id}", response_model=TransportJobResponse)
def get_job_details(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Fetch complete details of a specific transport job.
    Enforces that aggregators can only access their own assigned jobs.
    """
    job = db.query(TransportJob).filter(TransportJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transport job not found")

    if current_user.role == UserRole.AGGREGATOR and job.aggregator_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view another aggregator's job")

    return job


@router.post("/jobs/{job_id}/accept", response_model=TransportJobResponse)
def accept_transport_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.AGGREGATOR))
):
    """
    Aggregator accepts an assigned transport job.
    Changes job status to Accepted and moves it into Active Trips.
    Prevents duplicate acceptance or accepting another aggregator's job.
    """
    job = db.query(TransportJob).filter(TransportJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transport job not found")

    if job.aggregator_id and job.aggregator_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot accept a job assigned to another aggregator")

    if job.status == TransportStatus.ACCEPTED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Job has already been accepted")

    if job.status != TransportStatus.ASSIGNED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Cannot accept job in '{job.status}' status")

    job.aggregator_id = current_user.id
    job.status = TransportStatus.ACCEPTED
    job.notes = f"Accepted by {current_user.full_name} at {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}"

    # Update related Order status
    order = db.query(Order).filter(Order.id == job.order_id).first()
    if order and order.status in (OrderStatus.REQUESTED, OrderStatus.ACCEPTED):
        order.status = OrderStatus.COLLECTION_SCHEDULED

    db.commit()
    db.refresh(job)
    return job


@router.post("/jobs/{job_id}/reject", response_model=TransportJobResponse)
def reject_transport_job(
    job_id: int,
    payload: TransportRejectRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.AGGREGATOR))
):
    """
    Aggregator declines an assigned transport job with a mandatory rejection reason.
    Marks assignment as Rejected and makes it available for admin reassignment.
    """
    job = db.query(TransportJob).filter(TransportJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transport job not found")

    if job.aggregator_id and job.aggregator_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot reject another aggregator's job")

    if job.status not in (TransportStatus.ASSIGNED, TransportStatus.ACCEPTED):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Cannot reject a trip currently in '{job.status}' status")

    job.status = TransportStatus.REJECTED
    job.rejection_reason = payload.rejection_reason
    job.notes = f"Rejected by {current_user.full_name}: {payload.rejection_reason}"

    db.commit()
    db.refresh(job)
    return job


@router.post("/jobs/{job_id}/pickup", response_model=TransportJobResponse)
def confirm_pickup(
    job_id: int,
    payload: TransportPickupRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.AGGREGATOR))
):
    """
    Pickup Management: Collects agricultural waste from the farmer.
    Validates actual quantity collected:
    - Must be > 0.
    - Must not exceed expected quantity without approval.
    - Records discrepancy if actual < expected.
    - Prevents duplicate pickup submission.
    """
    job = db.query(TransportJob).filter(TransportJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transport job not found")

    if job.aggregator_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to submit pickup for this job")

    if job.status == TransportStatus.PICKED_UP:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Pickup has already been confirmed for this job")

    if job.status != TransportStatus.ACCEPTED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Job must be in 'Accepted' status to record pickup")

    # Quantity Validation
    actual = payload.actual_quantity
    expected = job.expected_quantity or 0.0

    if actual <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Actual collected quantity must be greater than zero")

    if expected > 0 and actual > expected:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Collected quantity ({actual} T) exceeds assigned quantity ({expected} T). Authorized approval required."
        )

    # Check for discrepancy
    if expected > 0 and actual < expected:
        diff = round(expected - actual, 2)
        job.discrepancy_flag = True
        job.discrepancy_reason = f"Actual collected quantity {actual} T is less than expected {expected} T (Difference: {diff} T recorded)"
    else:
        job.discrepancy_flag = False
        job.discrepancy_reason = None

    job.actual_quantity = actual
    job.picked_up_at = datetime.now(timezone.utc)
    job.status = TransportStatus.PICKED_UP
    if payload.notes:
        job.notes = payload.notes

    # Update corresponding OrderItem and Order
    if job.order_item_id:
        item = db.query(OrderItem).filter(OrderItem.id == job.order_item_id).first()
        if item:
            item.collected_quantity = actual
            item.farmer_status = "collected"

    order = db.query(Order).filter(Order.id == job.order_id).first()
    if order:
        order.status = OrderStatus.IN_TRANSIT

    db.commit()
    db.refresh(job)
    return job


@router.post("/jobs/{job_id}/deliver", response_model=TransportJobResponse)
def update_delivery_status(
    job_id: int,
    payload: TransportDeliverRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.AGGREGATOR))
):
    """
    Delivery Management: Updates status to Delivered after transporting to the buyer.
    Rules:
    - Cannot mark as Delivered before pickup is confirmed.
    - Aggregator CANNOT mark the order as Completed.
    - Only the buyer confirms receipt, which then moves the order to Completed.
    """
    job = db.query(TransportJob).filter(TransportJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transport job not found")

    if job.aggregator_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update delivery for this job")

    if job.status != TransportStatus.PICKED_UP and job.status != TransportStatus.IN_TRANSIT:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot mark as Delivered before pickup confirmation is recorded")

    job.status = TransportStatus.DELIVERED
    job.delivered_at = datetime.now(timezone.utc)
    if payload.notes:
        job.notes = payload.notes

    # Update related order to DELIVERED (Buyer confirmation pending)
    order = db.query(Order).filter(Order.id == job.order_id).first()
    if order:
        order.status = OrderStatus.DELIVERED
        for item in order.items:
            item.farmer_status = "delivered"
            if item.delivered_quantity is None:
                item.delivered_quantity = item.collected_quantity or item.committed_quantity

    db.commit()
    db.refresh(job)
    return job


@router.get("/history", response_model=List[TransportJobResponse])
def get_completed_trip_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.AGGREGATOR))
):
    """
    Completed Trips / Trip History:
    Displays only completed transport jobs assigned to the authenticated aggregator.
    Read-only history. Rejected and cancelled jobs are excluded.
    """
    return db.query(TransportJob).filter(
        TransportJob.aggregator_id == current_user.id,
        TransportJob.status.in_([TransportStatus.COMPLETED, TransportStatus.DELIVERED])
    ).order_by(desc(TransportJob.delivered_at)).all()


@router.get("/profile", response_model=AggregatorProfileResponse)
def get_aggregator_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.AGGREGATOR))
):
    """
    Aggregator Profile:
    Returns personal details and vehicle transportation details.
    """
    prof = current_user.aggregator_profile
    return AggregatorProfileResponse(
        id=current_user.id,
        username=current_user.username,
        full_name=current_user.full_name,
        email=current_user.email,
        phone_number=current_user.phone_number,
        operating_district=prof.operating_district if prof else None,
        vehicle_type=prof.vehicle_type if prof else "10T Eicher Commercial Truck",
        vehicle_number=prof.vehicle_number if prof else "GJ-01-AX-4821",
        capacity_tonnes=prof.capacity_tonnes if prof else 10.0,
        profile_id="AGY-TRN-3001"
    )


@router.put("/profile", response_model=AggregatorProfileResponse)
def update_aggregator_profile(
    payload: AggregatorProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.AGGREGATOR))
):
    """
    Aggregator Profile Update:
    Validates mobile number (10 digits) and email format.
    Saves vehicle and personal details. Prevents role modification.
    """
    if payload.full_name is not None and len(payload.full_name.strip()) > 0:
        current_user.full_name = payload.full_name.strip()

    if payload.phone_number is not None:
        clean_phone = re.sub(r'[\s\-\+\(\)]', '', payload.phone_number)
        if len(clean_phone) >= 10:
            current_user.phone_number = payload.phone_number.strip()
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Phone number must be at least 10 digits")

    if payload.email is not None:
        current_user.email = str(payload.email)

    prof = current_user.aggregator_profile
    if not prof:
        prof = AggregatorProfile(user_id=current_user.id)
        db.add(prof)

    if payload.operating_district is not None:
        prof.operating_district = payload.operating_district.strip()
    if payload.vehicle_type is not None:
        prof.vehicle_type = payload.vehicle_type.strip()
    if payload.vehicle_number is not None:
        prof.vehicle_number = payload.vehicle_number.strip().upper()

    db.commit()
    db.refresh(current_user)

    return AggregatorProfileResponse(
        id=current_user.id,
        username=current_user.username,
        full_name=current_user.full_name,
        email=current_user.email,
        phone_number=current_user.phone_number,
        operating_district=prof.operating_district,
        vehicle_type=prof.vehicle_type,
        vehicle_number=prof.vehicle_number,
        capacity_tonnes=prof.capacity_tonnes,
        profile_id="AGY-TRN-3001"
    )
