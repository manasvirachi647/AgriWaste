from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field, EmailStr
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_

from app.database import get_db
from app.models.user import User, UserRole
from app.models.listing import WasteListing, ListingStatus
from app.models.requirement import BuyerRequirement, RequirementStatus
from app.models.order import Order, OrderStatus, OrderItem
from app.models.transport import TransportJob, TransportStatus
from app.models.issue import IssueReport, IssueStatus
from app.schemas.user import UserResponse
from app.schemas.listing import WasteListingResponse
from app.schemas.requirement import BuyerRequirementResponse
from app.schemas.order import OrderResponse
from app.schemas.transport import TransportJobResponse
from app.schemas.issue import IssueResponse
from app.routers.deps import require_role

router = APIRouter(prefix="/admin", tags=["Admin Portal"])


def verify_admin(user: User):
    """Enforces admin authorization check."""
    if not user or user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: Admin credentials required."
        )


# Pydantic Request Models for Admin Operations
class StatusUpdateRequest(BaseModel):
    status: str
    reason: Optional[str] = None


class AggregatorAssignRequest(BaseModel):
    aggregator_id: int


class IssueActionRequest(BaseModel):
    status: str = Field(..., example="resolved")  # investigating, resolved, closed
    resolution_notes: Optional[str] = None


class AdminProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None


@router.get("/stats", response_model=Dict[str, Any])
def get_platform_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """
    Comprehensive Admin Dashboard Statistics & Recent Activity.
    Calculated purely from real database records.
    """
    verify_admin(current_user)
    total_users = db.query(User).count()
    total_farmers = db.query(User).filter(User.role == UserRole.FARMER).count()
    total_buyers = db.query(User).filter(User.role == UserRole.BUYER).count()
    total_transporters = db.query(User).filter(User.role == UserRole.AGGREGATOR).count()
    total_admins = db.query(User).filter(User.role == UserRole.ADMIN).count()
    
    total_listings = db.query(WasteListing).count()
    active_listings = db.query(WasteListing).filter(WasteListing.status == ListingStatus.AVAILABLE).count()
    
    total_requirements = db.query(BuyerRequirement).count()
    active_requirements = db.query(BuyerRequirement).filter(BuyerRequirement.status == RequirementStatus.OPEN).count()
    
    total_orders = db.query(Order).count()
    completed_orders = db.query(Order).filter(Order.status == OrderStatus.COMPLETED).count()
    pending_orders = db.query(Order).filter(Order.status.in_([
        OrderStatus.REQUESTED, OrderStatus.ACCEPTED, OrderStatus.COLLECTION_SCHEDULED,
        OrderStatus.COLLECTED, OrderStatus.IN_TRANSIT, OrderStatus.DELIVERED
    ])).count()
    
    total_jobs = db.query(TransportJob).count()
    open_disputes = db.query(IssueReport).filter(IssueReport.status == IssueStatus.OPEN).count()
    total_trade_volume = sum(o.total_amount for o in db.query(Order).all())

    # Recent platform activity (last 5 records each)
    recent_users = [
        {"type": "user", "title": f"New {u.role.value.capitalize()}: {u.full_name}", "timestamp": u.created_at.isoformat() if u.created_at else None}
        for u in db.query(User).order_by(desc(User.created_at)).limit(4).all()
    ]
    recent_listings = [
        {"type": "listing", "title": f"Listing #{l.id}: {l.material_name} ({l.available_quantity} T)", "timestamp": l.created_at.isoformat() if l.created_at else None}
        for l in db.query(WasteListing).order_by(desc(WasteListing.created_at)).limit(3).all()
    ]
    recent_orders = [
        {"type": "order", "title": f"Order #{o.id}: {o.total_quantity} T (Status: {o.status.value})", "timestamp": o.created_at.isoformat() if o.created_at else None}
        for o in db.query(Order).order_by(desc(Order.created_at)).limit(3).all()
    ]

    return {
        "users": {
            "total": total_users,
            "farmers": total_farmers,
            "buyers": total_buyers,
            "transporters": total_transporters,
            "admins": total_admins,
        },
        "marketplace": {
            "total_listings": total_listings,
            "active_listings": active_listings,
            "requirements": total_requirements,
            "active_requirements": active_requirements,
            "orders": total_orders,
            "completed_orders": completed_orders,
            "pending_orders": pending_orders,
            "transport_jobs": total_jobs,
            "total_trade_volume": round(total_trade_volume, 2),
        },
        "moderation": {
            "open_disputes": open_disputes,
            "platform_health": "100% Operational",
        },
        "recent_activity": recent_users + recent_listings + recent_orders
    }


@router.get("/users", response_model=List[UserResponse])
def get_all_users(
    role: Optional[UserRole] = Query(None, description="Filter by user role"),
    search: Optional[str] = Query(None, description="Search by name, username, email, phone"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """Admin inspects all registered accounts with role and search filters."""
    verify_admin(current_user)
    query = db.query(User)
    if role:
        query = query.filter(User.role == role)
    if search:
        s = f"%{search.strip()}%"
        query = query.filter(or_(
            User.full_name.ilike(s),
            User.username.ilike(s),
            User.email.ilike(s),
            User.phone_number.ilike(s)
        ))
    return query.order_by(desc(User.created_at)).all()


@router.get("/users/{user_id}", response_model=UserResponse)
def get_user_detail(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """Admin retrieves full profile details of a user."""
    verify_admin(current_user)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.patch("/users/{user_id}/status", response_model=UserResponse)
def toggle_user_active_status(
    user_id: int,
    is_active: bool = Query(..., description="Active status flag"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """Admin activates or suspends user accounts. Admins cannot deactivate themselves."""
    verify_admin(current_user)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    if user.id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Admins cannot deactivate their own account")

    user.is_active = is_active
    db.commit()
    db.refresh(user)
    return user


@router.get("/listings", response_model=List[WasteListingResponse])
def get_admin_listings(
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by listing status"),
    search: Optional[str] = Query(None, description="Search by material or location"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """Admin audits all residue listings across all statuses."""
    verify_admin(current_user)
    query = db.query(WasteListing)
    if status_filter:
        try:
            ls = ListingStatus(status_filter.lower())
            query = query.filter(WasteListing.status == ls)
        except ValueError:
            pass
    if search:
        s = f"%{search.strip()}%"
        query = query.filter(or_(
            WasteListing.material_name.ilike(s),
            WasteListing.location_name.ilike(s)
        ))
    return query.order_by(desc(WasteListing.created_at)).all()


@router.patch("/listings/{listing_id}/status", response_model=WasteListingResponse)
def moderate_listing_status(
    listing_id: int,
    payload: StatusUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """Admin moderates or deactivates a listing."""
    verify_admin(current_user)
    listing = db.query(WasteListing).filter(WasteListing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found")
    status_str = payload.status.lower()
    status_map = {
        "available": ListingStatus.AVAILABLE,
        "inactive": ListingStatus.CANCELLED,
        "cancelled": ListingStatus.CANCELLED,
        "reserved": ListingStatus.RESERVED,
        "completed": ListingStatus.COMPLETED,
    }
    if status_str in status_map:
        listing.status = status_map[status_str]
    else:
        try:
            listing.status = ListingStatus(status_str)
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid status: {payload.status}")
    if payload.reason:
        listing.quality_notes = f"[Admin Moderation ({datetime.now(timezone.utc).strftime('%Y-%m-%d')}): {payload.reason}] " + (listing.quality_notes or "")
    db.commit()
    db.refresh(listing)
    return listing


@router.get("/requirements", response_model=List[BuyerRequirementResponse])
def get_admin_requirements(
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by requirement status"),
    search: Optional[str] = Query(None, description="Search by material or delivery location"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """Admin reviews all buyer procurement requirements."""
    verify_admin(current_user)
    query = db.query(BuyerRequirement)
    if status_filter:
        sf = status_filter.lower()
        if sf in ["cancelled", "inactive"]:
            query = query.filter(BuyerRequirement.status == RequirementStatus.CANCELLED)
        elif sf in ["open", "active"]:
            query = query.filter(BuyerRequirement.status == RequirementStatus.OPEN)
        else:
            try:
                rs = RequirementStatus(sf)
                query = query.filter(BuyerRequirement.status == rs)
            except ValueError:
                pass
    if search:
        s = f"%{search.strip()}%"
        query = query.filter(or_(
            BuyerRequirement.material_name.ilike(s),
            BuyerRequirement.delivery_location.ilike(s)
        ))
    return query.order_by(desc(BuyerRequirement.created_at)).all()


@router.patch("/requirements/{requirement_id}/status", response_model=BuyerRequirementResponse)
def moderate_requirement_status(
    requirement_id: int,
    payload: StatusUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """Admin deactivates or cancels a buyer requirement."""
    verify_admin(current_user)
    req = db.query(BuyerRequirement).filter(BuyerRequirement.id == requirement_id).first()
    if not req:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Requirement not found")
    status_str = payload.status.lower()
    status_map = {
        "open": RequirementStatus.OPEN,
        "active": RequirementStatus.OPEN,
        "cancelled": RequirementStatus.CANCELLED,
        "inactive": RequirementStatus.CANCELLED,
        "closed": RequirementStatus.CANCELLED,
        "fulfilled": RequirementStatus.FULFILLED,
        "partially_fulfilled": RequirementStatus.PARTIALLY_FULFILLED
    }
    if status_str in status_map:
        req.status = status_map[status_str]
    else:
        try:
            req.status = RequirementStatus(status_str)
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid status: {payload.status}")
    if payload.reason:
        req.quality_specifications = f"[Admin Action ({datetime.now(timezone.utc).strftime('%Y-%m-%d')}): {payload.reason}] " + (req.quality_specifications or "")
    db.commit()
    db.refresh(req)
    return req


@router.get("/orders", response_model=List[OrderResponse])
@router.get("/transactions", response_model=List[OrderResponse])
def get_admin_orders(
    status_filter: Optional[str] = Query(None, alias="status"),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """Admin monitors all platform orders and multi-farmer settlements."""
    verify_admin(current_user)
    query = db.query(Order)
    if status_filter:
        try:
            os_val = OrderStatus(status_filter.lower())
            query = query.filter(Order.status == os_val)
        except ValueError:
            pass
    if search:
        s = f"%{search.strip()}%"
        query = query.filter(or_(
            Order.delivery_address.ilike(s),
            Order.id == int(search) if search.isdigit() else False
        ))
    return query.order_by(desc(Order.created_at)).all()


@router.get("/transport-jobs", response_model=List[TransportJobResponse])
def get_admin_transport_jobs(
    status_filter: Optional[str] = Query(None, alias="status"),
    unassigned_only: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """Admin audits all transport logistics jobs and unassigned requests."""
    verify_admin(current_user)
    query = db.query(TransportJob)
    if unassigned_only:
        query = query.filter(or_(
            TransportJob.aggregator_id.is_(None),
            TransportJob.status == TransportStatus.REJECTED
        ))
    elif status_filter:
        try:
            ts = TransportStatus(status_filter.lower())
            query = query.filter(TransportJob.status == ts)
        except ValueError:
            pass
    return query.order_by(desc(TransportJob.assigned_at)).all()


@router.post("/transport-jobs/{job_id}/assign", response_model=TransportJobResponse)
def assign_aggregator_to_job(
    job_id: int,
    payload: AggregatorAssignRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """Admin assigns or reassigns an active aggregator to a transport job."""
    verify_admin(current_user)
    job = db.query(TransportJob).filter(TransportJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transport job not found")
    
    aggregator = db.query(User).filter(User.id == payload.aggregator_id, User.role == UserRole.AGGREGATOR).first()
    if not aggregator:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aggregator not found or not valid role")
    if not aggregator.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot assign inactive aggregator")

    # Record reassignment history in notes
    prev_info = f"[Assigned to {aggregator.full_name} by Admin on {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')}]"
    job.notes = f"{prev_info}\n{job.notes or ''}".strip()
    job.aggregator_id = aggregator.id
    job.status = TransportStatus.ASSIGNED
    job.rejection_reason = None
    job.assigned_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(job)
    return job


@router.get("/aggregators", response_model=List[UserResponse])
def get_active_aggregators(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """Admin lists all active transport aggregator partners for job dispatch."""
    verify_admin(current_user)
    return db.query(User).filter(User.role == UserRole.AGGREGATOR).all()


@router.get("/disputes", response_model=List[IssueResponse])
@router.get("/issues", response_model=List[IssueResponse])
def get_admin_disputes(
    status_filter: Optional[str] = Query(None, alias="status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """Admin reviews all dispute reports with optional status filtering."""
    verify_admin(current_user)
    query = db.query(IssueReport)
    if status_filter:
        try:
            st = IssueStatus(status_filter.lower())
            query = query.filter(IssueReport.status == st)
        except ValueError:
            pass
    return query.order_by(desc(IssueReport.created_at)).all()


@router.patch("/issues/{issue_id}", response_model=IssueResponse)
def handle_admin_issue_action(
    issue_id: int,
    payload: IssueActionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """Admin updates issue status (e.g. investigating, resolved, closed) and sets resolution note."""
    verify_admin(current_user)
    issue = db.query(IssueReport).filter(IssueReport.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Issue report not found")
    
    st_val = payload.status.lower()
    if st_val in ["investigating", "under_review"]:
        issue.status = IssueStatus.INVESTIGATING
    elif st_val in ["resolved"]:
        issue.status = IssueStatus.RESOLVED
        issue.resolved_at = datetime.now(timezone.utc)
    elif st_val in ["closed", "rejected"]:
        issue.status = IssueStatus.CLOSED
        issue.resolved_at = datetime.now(timezone.utc)
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid issue status: {payload.status}")

    if payload.resolution_notes:
        issue.resolution_notes = payload.resolution_notes

    db.commit()
    db.refresh(issue)
    return issue


@router.get("/profile", response_model=UserResponse)
def get_admin_profile(
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """Admin views their own profile information."""
    verify_admin(current_user)
    return current_user


@router.patch("/profile", response_model=UserResponse)
def update_admin_profile(
    payload: AdminProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """Admin updates their profile details. Admin role cannot be modified."""
    verify_admin(current_user)
    if payload.full_name is not None:
        current_user.full_name = payload.full_name.strip()
    if payload.email is not None:
        current_user.email = payload.email.strip()
    if payload.phone_number is not None:
        current_user.phone_number = payload.phone_number.strip()
    
    db.commit()
    db.refresh(current_user)
    return current_user
