from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from app.models.requirement import RequirementStatus


class BuyerRequirementBase(BaseModel):
    material_name: str = Field(..., example="Rice Husk", min_length=2, max_length=100)
    required_quantity: float = Field(..., gt=0, example=20.0, description="Quantity required in given unit")
    unit: str = Field(default="tonnes", example="tonnes")
    target_price_min: Optional[float] = Field(default=None, ge=0, example=2200.0)
    target_price_max: Optional[float] = Field(default=None, ge=0, example=2600.0)
    delivery_location: str = Field(..., example="Sanand GIDC, Ahmedabad", min_length=2, max_length=200)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    required_by_date: Optional[datetime] = None
    quality_specifications: Optional[str] = Field(default=None, example="Moisture < 12%, clean, baled or loose")


class BuyerRequirementCreate(BuyerRequirementBase):
    pass


class BuyerRequirementUpdate(BaseModel):
    material_name: Optional[str] = None
    required_quantity: Optional[float] = Field(default=None, gt=0)
    target_price_min: Optional[float] = Field(default=None, ge=0)
    target_price_max: Optional[float] = Field(default=None, ge=0)
    delivery_location: Optional[str] = None
    required_by_date: Optional[datetime] = None
    quality_specifications: Optional[str] = None
    status: Optional[RequirementStatus] = None


class BuyerRequirementResponse(BuyerRequirementBase):
    id: int
    buyer_id: int
    fulfilled_quantity: float
    status: RequirementStatus
    created_at: datetime
    updated_at: datetime

    @property
    def remaining_quantity(self) -> float:
        return max(0.0, self.required_quantity - self.fulfilled_quantity)

    class Config:
        from_attributes = True
