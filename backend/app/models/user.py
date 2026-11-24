from datetime import datetime, timezone
import enum
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from app.database import Base


class UserRole(str, enum.Enum):
    FARMER = "farmer"
    BUYER = "buyer"
    AGGREGATOR = "aggregator"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    phone_number = Column(String(20), nullable=True)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.FARMER)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Profiles
    farmer_profile = relationship("FarmerProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    buyer_profile = relationship("BuyerProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    aggregator_profile = relationship("AggregatorProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")

    # Relationships
    listings = relationship("WasteListing", back_populates="farmer", foreign_keys="WasteListing.farmer_id")
    requirements = relationship("BuyerRequirement", back_populates="buyer", foreign_keys="BuyerRequirement.buyer_id")
    orders = relationship("Order", back_populates="buyer", foreign_keys="Order.buyer_id")


class FarmerProfile(Base):
    __tablename__ = "farmer_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    farm_village = Column(String(100), nullable=True)
    district = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    land_size_acres = Column(Float, nullable=True)
    primary_crops = Column(String(255), nullable=True)
    upi_id = Column(String(100), nullable=True)

    user = relationship("User", back_populates="farmer_profile")


class BuyerProfile(Base):
    __tablename__ = "buyer_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    company_name = Column(String(150), nullable=True)
    industry_type = Column(String(100), nullable=True)  # e.g., Biomass Energy, Paper, Composting
    facility_address = Column(Text, nullable=True)
    gst_number = Column(String(50), nullable=True)

    user = relationship("User", back_populates="buyer_profile")


class AggregatorProfile(Base):
    __tablename__ = "aggregator_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    vehicle_type = Column(String(100), nullable=True)  # e.g., Tractor Trolley, 10-Wheeler Truck
    vehicle_number = Column(String(50), nullable=True)  # Vehicle registration number e.g., GJ-01-AX-4821
    capacity_tonnes = Column(Float, nullable=True)
    operating_district = Column(String(100), nullable=True)
    service_radius_km = Column(Float, nullable=True, default=50.0)

    user = relationship("User", back_populates="aggregator_profile")
