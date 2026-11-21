from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from app.models.issue import IssueCategory, IssueStatus


class IssueCreate(BaseModel):
    order_id: Optional[int] = None
    category: IssueCategory = IssueCategory.QUALITY_MISMATCH
    title: str = Field(..., min_length=3, max_length=150, example="High moisture content detected at plant unloading")
    description: str = Field(..., min_length=5, example="Delivered husk had 18% moisture instead of agreed 12%.")


class IssueResolve(BaseModel):
    status: IssueStatus
    resolution_notes: str


class IssueResponse(BaseModel):
    id: int
    reporter_id: int
    order_id: Optional[int] = None
    category: IssueCategory
    title: str
    description: str
    status: IssueStatus
    resolution_notes: Optional[str] = None
    created_at: datetime
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True
