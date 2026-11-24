from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import get_db
from app.models.user import User, UserRole
from app.models.issue import IssueReport, IssueStatus
from app.schemas.issue import IssueCreate, IssueResponse, IssueResolve
from app.routers.deps import get_current_user, require_role

router = APIRouter(prefix="/issues", tags=["Dispute & Issue Reporting"])


from app.models.order import Order

@router.post("", response_model=IssueResponse, status_code=status.HTTP_201_CREATED)
def report_issue(
    payload: IssueCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Week 7: Report a dispute, weight mismatch, or delivery issue.
    Validates association with the reporter's order if order_id is provided.
    """
    if payload.order_id:
        order = db.query(Order).filter(Order.id == payload.order_id).first()
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Referenced order does not exist")
        # Ensure user has a relationship to this order if not admin
        if current_user.role != UserRole.ADMIN:
            is_buyer = order.buyer_id == current_user.id
            is_farmer = any(item.farmer_id == current_user.id for item in order.items)
            is_transporter = any(job.aggregator_id == current_user.id for job in order.transport_jobs)
            if not (is_buyer or is_farmer or is_transporter):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authorized to file a dispute on an order you are not a party to"
                )

    issue = IssueReport(
        reporter_id=current_user.id,
        order_id=payload.order_id,
        category=payload.category,
        title=payload.title.strip(),
        description=payload.description.strip(),
        status=IssueStatus.OPEN,
    )
    db.add(issue)
    db.commit()
    db.refresh(issue)
    return issue


@router.get("", response_model=List[IssueResponse])
def get_issues(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List issues. Users see issues they reported; Admins see all issues."""
    query = db.query(IssueReport)
    if current_user.role != UserRole.ADMIN:
        query = query.filter(IssueReport.reporter_id == current_user.id)
    return query.order_by(desc(IssueReport.created_at)).all()


@router.patch("/{issue_id}/resolve", response_model=IssueResponse)
def resolve_issue(
    issue_id: int,
    payload: IssueResolve,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """Admin resolves a dispute ticket."""
    issue = db.query(IssueReport).filter(IssueReport.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Issue report not found")

    issue.status = payload.status
    issue.resolution_notes = payload.resolution_notes
    issue.resolved_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(issue)
    return issue
