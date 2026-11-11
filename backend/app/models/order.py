from datetime import datetime, timezone
import enum
from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base


class OrderStatus(str, enum.Enum):
    REQUESTED = "requested"
    ACCEPTED = "accepted"
    COLLECTION_SCHEDULED = "collection_scheduled"
    COLLECTED = "collected"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    buyer_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    requirement_id = Column(Integer, ForeignKey("buyer_requirements.id"), nullable=True)

    total_quantity = Column(Float, nullable=False)
    unit = Column(String(20), nullable=False, default="tonnes")
    total_amount = Column(Float, nullable=False)
    
    delivery_address = Column(Text, nullable=False)
    status = Column(Enum(OrderStatus), default=OrderStatus.REQUESTED, nullable=False)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    buyer = relationship("User", back_populates="orders")
    requirement = relationship("BuyerRequirement", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    transport_jobs = relationship("TransportJob", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    """Represents an individual farmer's contribution to a buyer order (multi-farmer fulfillment)."""
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    listing_id = Column(Integer, ForeignKey("waste_listings.id"), nullable=False, index=True)
    farmer_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    committed_quantity = Column(Float, nullable=False)
    collected_quantity = Column(Float, nullable=True)
    delivered_quantity = Column(Float, nullable=True)
    price_per_unit = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=False)

    farmer_status = Column(String(50), default="pending")  # pending, accepted, collected, delivered, rejected
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    order = relationship("Order", back_populates="items")
    listing = relationship("WasteListing", back_populates="order_items")
    farmer = relationship("User")
