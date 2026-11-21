from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import get_db
from app.models.user import User, UserRole
from app.models.order import Order, OrderItem, OrderStatus
from app.schemas.order import OrderCreateAllocationRequest, OrderResponse, OrderStatusUpdate
from app.services.allocation import allocate_multi_farmer_order
from app.routers.deps import get_current_user, require_role

router = APIRouter(prefix="/orders", tags=["Orders & Multi-Farmer Allocation"])


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    payload: OrderCreateAllocationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.BUYER))
):
    """
    Week 5 & 6: Create Multi-Farmer Order
    Combines selected farmer contributions into one order, deducting inventory safely.
    """
    contributions_dict = [
        {"listing_id": c.listing_id, "allocated_quantity": c.allocated_quantity}
        for c in payload.contributions
    ]
    order = allocate_multi_farmer_order(
        db=db,
        buyer=current_user,
        requirement_id=payload.requirement_id,
        contributions=contributions_dict,
        delivery_address=payload.delivery_address
    )
    return order


@router.get("", response_model=List[OrderResponse])
def get_orders(
    status_filter: Optional[OrderStatus] = Query(None, alias="status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List orders based on user role:
    - Buyers see their own orders.
    - Farmers see orders where they contributed items.
    - Transporters / Admins see all platform orders.
    """
    query = db.query(Order)
    
    if current_user.role == UserRole.BUYER:
        query = query.filter(Order.buyer_id == current_user.id)
    elif current_user.role == UserRole.FARMER:
        query = query.join(OrderItem).filter(OrderItem.farmer_id == current_user.id).distinct()
    
    if status_filter:
        query = query.filter(Order.status == status_filter)

    return query.order_by(desc(Order.created_at)).all()


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get single order details."""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    
    # Ownership verification
    if current_user.role == UserRole.BUYER and order.buyer_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this order")
    
    return order


@router.patch("/{order_id}/status", response_model=OrderResponse)
def update_order_status(
    order_id: int,
    payload: OrderStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Advance order through lifecycle statuses."""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    order.status = payload.status
    db.commit()
    db.refresh(order)
    return order
