from datetime import datetime
from typing import List, Optional, Any
from pydantic import BaseModel, Field
from app.models.order import OrderStatus


class OrderContributionItem(BaseModel):
    listing_id: int
    allocated_quantity: float = Field(..., gt=0, example=2.5)


class OrderCreateAllocationRequest(BaseModel):
    requirement_id: int
    contributions: List[OrderContributionItem]
    delivery_address: str = Field(..., example="Sanand GIDC Biofuel Plant, Ahmedabad")


class OrderItemResponse(BaseModel):
    id: int
    order_id: int
    listing_id: int
    farmer_id: int
    committed_quantity: float
    collected_quantity: Optional[float] = None
    delivered_quantity: Optional[float] = None
    price_per_unit: float
    subtotal: float
    farmer_status: str

    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    id: int
    buyer_id: int
    requirement_id: Optional[int] = None
    total_quantity: float
    unit: str
    total_amount: float
    delivery_address: str
    status: OrderStatus
    created_at: datetime
    updated_at: datetime
    items: List[OrderItemResponse] = []

    class Config:
        from_attributes = True


class OrderStatusUpdate(BaseModel):
    status: OrderStatus
