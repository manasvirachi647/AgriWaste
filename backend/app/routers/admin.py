from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, UserRole
from app.models.listing import WasteListing
from app.models.requirement import BuyerRequirement
from app.models.order import Order
from app.models.transport import TransportJob
from app.models.issue import IssueReport, IssueStatus
from app.schemas.user import UserResponse
from app.routers.deps import require_role

router = APIRouter(prefix="/admin", tags=["Admin Portal"])


@router.get("/stats", response_model=Dict[str, Any])
def get_platform_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """
    Week 7: Admin Overview Dashboard Statistics
    """
    total_users = db.query(User).count()
    total_farmers = db.query(User).filter(User.role == UserRole.FARMER).count()
    total_buyers = db.query(User).filter(User.role == UserRole.BUYER).count()
    total_transporters = db.query(User).filter(User.role == UserRole.AGGREGATOR).count()
    
    total_listings = db.query(WasteListing).count()
    total_requirements = db.query(BuyerRequirement).count()
    total_orders = db.query(Order).count()
    total_jobs = db.query(TransportJob).count()
    open_disputes = db.query(IssueReport).filter(IssueReport.status == IssueStatus.OPEN).count()

    return {
        "users": {
            "total": total_users,
            "farmers": total_farmers,
            "buyers": total_buyers,
            "transporters": total_transporters,
        },
        "marketplace": {
            "listings": total_listings,
            "requirements": total_requirements,
            "orders": total_orders,
            "transport_jobs": total_jobs,
        },
        "moderation": {
            "open_disputes": open_disputes,
            "platform_health": "100% Operational",
        }
    }


@router.get("/users", response_model=List[UserResponse])
def get_all_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """Admin inspects all registered accounts."""
    return db.query(User).all()
