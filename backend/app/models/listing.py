from datetime import datetime, timezone
import enum
from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base


class ListingStatus(str, enum.Enum):
    AVAILABLE = "available"
    PARTIALLY_RESERVED = "partially_reserved"
    RESERVED = "reserved"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class WasteListing(Base):
    __tablename__ = "waste_listings"

    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Residue info
    material_name = Column(String(100), nullable=False, index=True)  # e.g., Rice Husk, Wheat Straw, Cotton Stalks
    estimated_quantity = Column(Float, nullable=False)
    available_quantity = Column(Float, nullable=False)  # remaining uncommitted quantity
    verified_quantity = Column(Float, nullable=True)     # verified at collection
    unit = Column(String(20), nullable=False, default="tonnes")  # tonnes, kg, quintals
    price_per_unit = Column(Float, nullable=False)      # Expected price
    
    # Location
    location_name = Column(String(150), nullable=False)  # Village / Town / District
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    # Timing
    available_from = Column(DateTime, nullable=True)
    available_until = Column(DateTime, nullable=True)
    
    # Quality & Storage
    storage_type = Column(String(100), nullable=True)   # Dry covered shed, Open field, Silo
    moisture_condition = Column(String(100), nullable=True)  # Low, Medium, High / Dry, Semi-dry
    quality_notes = Column(Text, nullable=True)
    photo_urls = Column(Text, nullable=True)            # Comma-separated or JSON list of image URLs
    
    # Status
    status = Column(Enum(ListingStatus), default=ListingStatus.AVAILABLE, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    farmer = relationship("User", back_populates="listings")
    order_items = relationship("OrderItem", back_populates="listing")
