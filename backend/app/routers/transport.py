from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import get_db
from app.models.user import User, UserRole
from app.models.transport import TransportJob, TransportStatus
from app.models.order import Order, OrderStatus
from app.schemas.transport import TransportJobResponse, TransportStatusUpdate
from app.routers.deps import get_current_user, require_role

router = APIRouter(prefix="/transport", tags=["Logistics & Transport Jobs"])


@router.get("/jobs", response_model=List[TransportJobResponse])
def get_transport_jobs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Week 6: Lists transport assignments.
    Transporters see jobs assigned to them or unassigned available jobs.
    """
    query = db.query(TransportJob)
    if current_user.role == UserRole.AGGREGATOR:
        query = query.filter(
            (TransportJob.aggregator_id == current_user.id) |
            (TransportJob.aggregator_id.is_(None))
        )
    return query.order_by(desc(TransportJob.assigned_at)).all()


@router.get("/jobs/{job_id}", response_model=TransportJobResponse)
def get_job(job_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Fetch details of a specific transport job."""
    job = db.query(TransportJob).filter(TransportJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transport job not found")
    return job


@router.post("/jobs/{job_id}/claim", response_model=TransportJobResponse)
def claim_transport_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.AGGREGATOR))
):
    """Transporter accepts / claims an unassigned transport job."""
    job = db.query(TransportJob).filter(TransportJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transport job not found")
    
    if job.aggregator_id and job.aggregator_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Job has already been claimed by another transporter")

    job.aggregator_id = current_user.id
    job.status = TransportStatus.PICKUP_IN_PROGRESS
    
    # Also update related order status
    order = db.query(Order).filter(Order.id == job.order_id).first()
    if order:
        order.status = OrderStatus.COLLECTION_SCHEDULED

    db.commit()
    db.refresh(job)
    return job


@router.patch("/jobs/{job_id}/status", response_model=TransportJobResponse)
def update_transport_status(
    job_id: int,
    payload: TransportStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Transporter updates pickup, transit, or delivery progress with RBAC validation."""
    job = db.query(TransportJob).filter(TransportJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transport job not found")

    # Only the assigned transporter or an admin is authorized to update job status
    if job.aggregator_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this transport job"
        )

    job.status = payload.status
    if payload.notes:
        job.notes = payload.notes

    if payload.status == TransportStatus.DELIVERED:
        job.delivered_at = datetime.now(timezone.utc)
        order = db.query(Order).filter(Order.id == job.order_id).first()
        if order:
            order.status = OrderStatus.DELIVERED
            # Also update order items to delivered
            for item in order.items:
                item.farmer_status = "delivered"
                if item.delivered_quantity is None:
                    item.delivered_quantity = item.committed_quantity

    db.commit()
    db.refresh(job)
    return job
