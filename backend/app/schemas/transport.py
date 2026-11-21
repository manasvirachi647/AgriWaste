from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.models.transport import TransportStatus


class TransportJobResponse(BaseModel):
    id: int
    order_id: int
    aggregator_id: Optional[int] = None
    pickup_locations_json: str
    dropoff_location: str
    estimated_distance_km: Optional[float] = None
    estimated_cost: Optional[float] = None
    actual_cost: Optional[float] = None
    status: TransportStatus
    notes: Optional[str] = None
    assigned_at: datetime
    delivered_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TransportStatusUpdate(BaseModel):
    status: TransportStatus
    notes: Optional[str] = None
