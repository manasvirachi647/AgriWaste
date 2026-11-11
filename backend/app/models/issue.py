from datetime import datetime, timezone
import enum
from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base


class IssueCategory(str, enum.Enum):
    QUALITY_MISMATCH = "quality_mismatch"
    QUANTITY_DISCREPANCY = "quantity_discrepancy"
    TRANSPORT_DELAY = "transport_delay"
    PAYMENT_DISPUTE = "payment_dispute"
    OTHER = "other"


class IssueStatus(str, enum.Enum):
    OPEN = "open"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    CLOSED = "closed"


class IssueReport(Base):
    __tablename__ = "issue_reports"

    id = Column(Integer, primary_key=True, index=True)
    reporter_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)

    category = Column(Enum(IssueCategory), nullable=False)
    title = Column(String(150), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(Enum(IssueStatus), default=IssueStatus.OPEN, nullable=False)
    resolution_notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    resolved_at = Column(DateTime, nullable=True)

    reporter = relationship("User")
    order = relationship("Order")
