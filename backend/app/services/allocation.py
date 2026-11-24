import json
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.listing import WasteListing, ListingStatus
from app.models.requirement import BuyerRequirement, RequirementStatus
from app.models.order import Order, OrderItem, OrderStatus
from app.models.transport import TransportJob, TransportStatus
from app.models.user import User


def allocate_multi_farmer_order(
    db: Session,
    buyer: User,
    requirement_id: int,
    contributions: List[Dict[str, Any]],  # [{"listing_id": 1, "allocated_quantity": 2.5}]
    delivery_address: str
) -> Order:
    """
    Core USP Feature (Section 6.5 & Phase 11):
    Fulfils a large industrial buyer requirement using contributions from multiple farmers.
    Handles quantity deduction safely in a database transaction to prevent double booking.
    """
    req = db.query(BuyerRequirement).filter(BuyerRequirement.id == requirement_id).first()
    if not req:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Buyer requirement not found")
    
    if req.buyer_id != buyer.id and buyer.role.value != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to fulfill this requirement")

    if req.status in [RequirementStatus.CANCELLED, RequirementStatus.FULFILLED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot allocate order for a requirement that is already {req.status.value}."
        )

    total_allocated_qty = 0.0
    total_amount = 0.0
    order_items_to_create = []
    pickup_locations = []

    try:
        for item in contributions:
            listing_id = item.get("listing_id")
            alloc_qty = float(item.get("allocated_quantity", 0.0))

            if alloc_qty <= 0:
                continue

            # Fetch listing and lock/validate
            listing = db.query(WasteListing).filter(WasteListing.id == listing_id).first()
            if not listing:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Residue listing #{listing_id} not found"
                )

            if listing.status != ListingStatus.AVAILABLE and listing.status != ListingStatus.PARTIALLY_RESERVED:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Listing #{listing_id} ({listing.material_name}) is no longer available for booking."
                )

            if listing.available_quantity < alloc_qty:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Insufficient quantity on listing #{listing_id} ({listing.material_name}). Requested {alloc_qty} {listing.unit}, but only {listing.available_quantity} {listing.unit} is available."
                )

            # Deduct listing available quantity safely
            listing.available_quantity = round(listing.available_quantity - alloc_qty, 3)
            if listing.available_quantity <= 0.001:
                listing.available_quantity = 0.0
                listing.status = ListingStatus.RESERVED
            else:
                listing.status = ListingStatus.PARTIALLY_RESERVED

            subtotal = round(alloc_qty * listing.price_per_unit, 2)
            total_allocated_qty += alloc_qty
            total_amount += subtotal

            order_items_to_create.append({
                "listing_id": listing.id,
                "farmer_id": listing.farmer_id,
                "committed_quantity": alloc_qty,
                "price_per_unit": listing.price_per_unit,
                "subtotal": subtotal,
            })

            pickup_locations.append({
                "listing_id": listing.id,
                "farmer_id": listing.farmer_id,
                "location": listing.location_name,
                "material": listing.material_name,
                "quantity": alloc_qty,
                "unit": listing.unit,
            })

        if total_allocated_qty <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Total allocated quantity must be greater than 0"
            )

        # Create Main Order
        new_order = Order(
            buyer_id=buyer.id,
            requirement_id=req.id,
            total_quantity=round(total_allocated_qty, 2),
            unit=req.unit,
            total_amount=round(total_amount, 2),
            delivery_address=delivery_address.strip() or req.delivery_location,
            status=OrderStatus.REQUESTED,
        )
        db.add(new_order)
        db.flush()  # obtain new_order.id

        # Create Order Items
        for oi in order_items_to_create:
            order_item = OrderItem(
                order_id=new_order.id,
                listing_id=oi["listing_id"],
                farmer_id=oi["farmer_id"],
                committed_quantity=oi["committed_quantity"],
                price_per_unit=oi["price_per_unit"],
                subtotal=oi["subtotal"],
                farmer_status="accepted",
            )
            db.add(order_item)

        # Update Requirement fulfillment
        req.fulfilled_quantity = round((req.fulfilled_quantity or 0.0) + total_allocated_qty, 2)
        if req.fulfilled_quantity >= req.required_quantity:
            req.status = RequirementStatus.FULFILLED
        else:
            req.status = RequirementStatus.PARTIALLY_FULFILLED

        # Automatically generate Transport Job
        estimated_km = round(len(pickup_locations) * 22.5 + 15.0, 1)  # Heuristic distance estimation
        estimated_transport_cost = round(estimated_km * 35.0, 2)       # Approx ₹35/km commercial rate

        transport_job = TransportJob(
            order_id=new_order.id,
            pickup_locations_json=json.dumps(pickup_locations),
            dropoff_location=new_order.delivery_address,
            estimated_distance_km=estimated_km,
            estimated_cost=estimated_transport_cost,
            status=TransportStatus.ASSIGNED,
            notes=f"Aggregated pickup from {len(pickup_locations)} rural farms."
        )
        db.add(transport_job)

        db.commit()
        db.refresh(new_order)
        return new_order
    except Exception:
        db.rollback()
        raise
