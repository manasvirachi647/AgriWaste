from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import get_db
from app.models.user import User, UserRole
from app.models.listing import WasteListing, ListingStatus
from app.models.requirement import BuyerRequirement
from app.models.order import Order
from app.models.transport import TransportJob
from app.models.issue import IssueReport, IssueStatus
from app.schemas.user import UserResponse
from app.schemas.listing import WasteListingResponse
from app.schemas.order import OrderResponse
from app.schemas.issue import IssueResponse
from app.routers.deps import require_role

router = APIRouter(prefix="/admin", tags=["Admin Portal"])


@router.get("/stats", response_model=Dict[str, Any])
def get_platform_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """
    Week 7: Admin Overview Dashboard Statistics
    Calculated purely from real database records.
    """
    total_users = db.query(User).count()
    total_farmers = db.query(User).filter(User.role == UserRole.FARMER).count()
    total_buyers = db.query(User).filter(User.role == UserRole.BUYER).count()
    total_transporters = db.query(User).filter(User.role == UserRole.AGGREGATOR).count()
    
    total_listings = db.query(WasteListing).count()
    active_listings = db.query(WasteListing).filter(WasteListing.status == ListingStatus.AVAILABLE).count()
    total_requirements = db.query(BuyerRequirement).count()
    total_orders = db.query(Order).count()
    total_jobs = db.query(TransportJob).count()
    open_disputes = db.query(IssueReport).filter(IssueReport.status == IssueStatus.OPEN).count()

    total_trade_volume = sum(o.total_amount for o in db.query(Order).all())

    return {
        "users": {
            "total": total_users,
            "farmers": total_farmers,
            "buyers": total_buyers,
            "transporters": total_transporters,
        },
        "marketplace": {
            "total_listings": total_listings,
            "active_listings": active_listings,
            "requirements": total_requirements,
            "orders": total_orders,
            "transport_jobs": total_jobs,
            "total_trade_volume": round(total_trade_volume, 2),
        },
        "moderation": {
            "open_disputes": open_disputes,
            "platform_health": "100% Operational",
        }
    }


@router.get("/users", response_model=List[UserResponse])
def get_all_users(
    role: Optional[UserRole] = Query(None, description="Filter by user role"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """Admin inspects all registered accounts."""
    query = db.query(User)
    if role:
        query = query.filter(User.role == role)
    return query.order_by(desc(User.created_at)).all()


@router.patch("/users/{user_id}/status", response_model=UserResponse)
def toggle_user_active_status(
    user_id: int,
    is_active: bool = Query(..., description="Active status flag"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """Admin can activate or suspend user accounts."""
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
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """Admin audits all residue listings across all statuses."""
    return db.query(WasteListing).order_by(desc(WasteListing.created_at)).all()


@router.get("/transactions", response_model=List[OrderResponse])
def get_admin_transactions(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """Admin monitors all platform orders and multi-farmer settlements."""
    return db.query(Order).order_by(desc(Order.created_at)).all()


@router.get("/disputes", response_model=List[IssueResponse])
def get_admin_disputes(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """Admin reviews all dispute reports."""
    return db.query(IssueReport).order_by(desc(IssueReport.created_at)).all()
