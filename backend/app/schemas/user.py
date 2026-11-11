from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr
from app.models.user import UserRole


class FarmerProfileBase(BaseModel):
    farm_village: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    land_size_acres: Optional[float] = None
    primary_crops: Optional[str] = None
    upi_id: Optional[str] = None


class FarmerProfileResponse(FarmerProfileBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True


class BuyerProfileBase(BaseModel):
    company_name: Optional[str] = None
    industry_type: Optional[str] = None
    facility_address: Optional[str] = None
    gst_number: Optional[str] = None


class BuyerProfileResponse(BuyerProfileBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True


class AggregatorProfileBase(BaseModel):
    vehicle_type: Optional[str] = None
    capacity_tonnes: Optional[float] = None
    operating_district: Optional[str] = None
    service_radius_km: Optional[float] = 50.0


class AggregatorProfileResponse(AggregatorProfileBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: str
    phone_number: Optional[str] = None
    role: UserRole = UserRole.FARMER


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    farmer_profile: Optional[FarmerProfileResponse] = None
    buyer_profile: Optional[BuyerProfileResponse] = None
    aggregator_profile: Optional[AggregatorProfileResponse] = None

    class Config:
        from_attributes = True
