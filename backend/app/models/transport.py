from datetime import datetime, timezone
import enum
from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base


class TransportStatus(str, enum.Enum):
    ASSIGNED = "assigned"
    PICKUP_IN_PROGRESS = "pickup_in_progress"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class TransportJob(Base):
    __tablename__ = "transport_jobs"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    aggregator_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)

    pickup_locations_json = Column(Text, nullable=False)  # JSON list of pickup locations & quantities
    dropoff_location = Column(String(200), nullable=False)
    
    estimated_distance_km = Column(Float, nullable=True)
    estimated_cost = Column(Float, nullable=True)
    actual_cost = Column(Float, nullable=True)
    
    status = Column(Enum(TransportStatus), default=TransportStatus.ASSIGNED, nullable=False)
    notes = Column(Text, nullable=True)
    
    assigned_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    delivered_at = Column(DateTime, nullable=True)

    order = relationship("Order", back_populates="transport_jobs")
    aggregator = relationship("User")
