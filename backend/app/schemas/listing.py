from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from app.models.listing import ListingStatus


class WasteListingBase(BaseModel):
    material_name: str = Field(..., example="Rice Husk")
    estimated_quantity: float = Field(..., gt=0, example=2.5)
    unit: str = Field(default="tonnes", example="tonnes")
    price_per_unit: float = Field(..., gt=0, example=2500.0)
    location_name: str = Field(..., example="Ahmedabad, Gujarat")
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    available_from: Optional[datetime] = None
    available_until: Optional[datetime] = None
    storage_type: Optional[str] = Field(default=None, example="Dry covered shed")
    moisture_condition: Optional[str] = Field(default=None, example="Low moisture / Dry")
    quality_notes: Optional[str] = None
    photo_urls: Optional[str] = None


class WasteListingCreate(WasteListingBase):
    pass


class WasteListingUpdate(BaseModel):
    material_name: Optional[str] = None
    estimated_quantity: Optional[float] = Field(None, gt=0)
    available_quantity: Optional[float] = Field(None, ge=0)
    price_per_unit: Optional[float] = Field(None, gt=0)
    location_name: Optional[str] = None
    storage_type: Optional[str] = None
    moisture_condition: Optional[str] = None
    quality_notes: Optional[str] = None
    status: Optional[ListingStatus] = None


class WasteListingResponse(WasteListingBase):
    id: int
    farmer_id: int
    available_quantity: float
    verified_quantity: Optional[float] = None
    status: ListingStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
