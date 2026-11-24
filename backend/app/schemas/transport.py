from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr
from app.models.transport import TransportStatus


class TransportJobResponse(BaseModel):
    id: int
    order_id: int
    order_item_id: Optional[int] = None
    aggregator_id: Optional[int] = None
    
    farmer_id: Optional[int] = None
    farmer_name: Optional[str] = None
    farmer_phone: Optional[str] = None
    
    buyer_id: Optional[int] = None
    buyer_name: Optional[str] = None
    buyer_phone: Optional[str] = None
    
    waste_type: Optional[str] = None
    expected_quantity: Optional[float] = None
    actual_quantity: Optional[float] = None
    discrepancy_flag: Optional[bool] = False
    discrepancy_reason: Optional[str] = None
    
    pickup_location: Optional[str] = None
    delivery_location: Optional[str] = None
    scheduled_pickup_date: Optional[str] = None
    rejection_reason: Optional[str] = None

    pickup_locations_json: Optional[str] = "[]"
    dropoff_location: Optional[str] = None
    estimated_distance_km: Optional[float] = None
    estimated_cost: Optional[float] = None
    actual_cost: Optional[float] = None
    
    status: TransportStatus
    notes: Optional[str] = None
    assigned_at: datetime
    picked_up_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TransportStatusUpdate(BaseModel):
    status: TransportStatus
    notes: Optional[str] = None


class TransportRejectRequest(BaseModel):
    rejection_reason: str = Field(..., min_length=3, description="Mandatory reason for declining the transport job")


class TransportPickupRequest(BaseModel):
    actual_quantity: float = Field(..., gt=0, description="Actual agricultural waste collected in tonnes")
    notes: Optional[str] = None


class TransportDeliverRequest(BaseModel):
    notes: Optional[str] = None


class AggregatorStatsResponse(BaseModel):
    total_assigned: int
    pending_pickups: int
    pending_deliveries: int
    completed_trips: int


class AggregatorProfileResponse(BaseModel):
    id: int
    username: str
    full_name: str
    email: str
    phone_number: Optional[str] = None
    operating_district: Optional[str] = None
    vehicle_type: Optional[str] = None
    vehicle_number: Optional[str] = None
    capacity_tonnes: Optional[float] = None
    profile_id: Optional[str] = "AGY-TRN-3001"


class AggregatorProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None
    operating_district: Optional[str] = None
    vehicle_type: Optional[str] = None
    vehicle_number: Optional[str] = None
