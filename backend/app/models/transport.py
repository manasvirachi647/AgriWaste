from datetime import datetime, timezone
import enum
from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from app.database import Base


class TransportStatus(str, enum.Enum):
    ASSIGNED = "assigned"
    ACCEPTED = "accepted"
    PICKED_UP = "picked_up"
    PICKUP_IN_PROGRESS = "pickup_in_progress"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    COMPLETED = "completed"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class TransportJob(Base):
    __tablename__ = "transport_jobs"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    order_item_id = Column(Integer, ForeignKey("order_items.id", ondelete="SET NULL"), nullable=True)
    aggregator_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)

    farmer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    farmer_name = Column(String(100), nullable=True)
    farmer_phone = Column(String(50), nullable=True)

    buyer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    buyer_name = Column(String(100), nullable=True)
    buyer_phone = Column(String(50), nullable=True)

    waste_type = Column(String(100), nullable=True)
    expected_quantity = Column(Float, nullable=True)
    actual_quantity = Column(Float, nullable=True)
    discrepancy_flag = Column(Boolean, default=False)
    discrepancy_reason = Column(Text, nullable=True)

    pickup_location = Column(String(255), nullable=True)
    delivery_location = Column(String(255), nullable=True)
    scheduled_pickup_date = Column(String(50), nullable=True)
    rejection_reason = Column(Text, nullable=True)

    pickup_locations_json = Column(Text, nullable=True, default="[]")  # JSON list of pickup locations & quantities
    dropoff_location = Column(String(200), nullable=True)
    
    estimated_distance_km = Column(Float, nullable=True)
    estimated_cost = Column(Float, nullable=True)
    actual_cost = Column(Float, nullable=True)
    
    status = Column(Enum(TransportStatus), default=TransportStatus.ASSIGNED, nullable=False)
    notes = Column(Text, nullable=True)
    
    assigned_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    picked_up_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    order = relationship("Order", back_populates="transport_jobs")
    order_item = relationship("OrderItem")
    aggregator = relationship("User", foreign_keys=[aggregator_id])
    farmer = relationship("User", foreign_keys=[farmer_id])
    buyer = relationship("User", foreign_keys=[buyer_id])
