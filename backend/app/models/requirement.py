from datetime import datetime, timezone
import enum
from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base


class RequirementStatus(str, enum.Enum):
    OPEN = "open"
    PARTIALLY_FULFILLED = "partially_fulfilled"
    FULFILLED = "fulfilled"
    CANCELLED = "cancelled"


class BuyerRequirement(Base):
    __tablename__ = "buyer_requirements"

    id = Column(Integer, primary_key=True, index=True)
    buyer_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    material_name = Column(String(100), nullable=False, index=True)
    required_quantity = Column(Float, nullable=False)
    fulfilled_quantity = Column(Float, default=0.0)
    unit = Column(String(20), nullable=False, default="tonnes")

    target_price_min = Column(Float, nullable=True)
    target_price_max = Column(Float, nullable=True)

    delivery_location = Column(String(200), nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    required_by_date = Column(DateTime, nullable=True)
    quality_specifications = Column(Text, nullable=True)
    
    status = Column(Enum(RequirementStatus), default=RequirementStatus.OPEN, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    buyer = relationship("User", back_populates="requirements")
    matches = relationship("Match", back_populates="requirement", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="requirement")
