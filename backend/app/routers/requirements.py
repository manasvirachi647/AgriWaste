from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import get_db
from app.models.user import User, UserRole
from app.models.requirement import BuyerRequirement, RequirementStatus
from app.models.listing import WasteListing, ListingStatus
from app.schemas.requirement import (
    BuyerRequirementCreate,
    BuyerRequirementUpdate,
    BuyerRequirementResponse,
)
from app.schemas.listing import WasteListingResponse
from app.routers.deps import get_current_user, require_role

router = APIRouter(prefix="/requirements", tags=["Buyer Requirements"])


@router.post("", response_model=BuyerRequirementResponse, status_code=status.HTTP_201_CREATED)
def create_requirement(
    data: BuyerRequirementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.BUYER))
):
    """Publish a new industrial biomass requirement. Buyer ID is taken securely from JWT."""
    requirement = BuyerRequirement(
        buyer_id=current_user.id,
        material_name=data.material_name.strip(),
        required_quantity=data.required_quantity,
        fulfilled_quantity=0.0,
        unit=data.unit,
        target_price_min=data.target_price_min,
        target_price_max=data.target_price_max,
        delivery_location=data.delivery_location.strip(),
        latitude=data.latitude,
        longitude=data.longitude,
        required_by_date=data.required_by_date,
        quality_specifications=data.quality_specifications,
        status=RequirementStatus.OPEN,
    )
    db.add(requirement)
    db.commit()
    db.refresh(requirement)
    return requirement


@router.get("", response_model=List[BuyerRequirementResponse])
def get_all_requirements(
    material: Optional[str] = Query(None, description="Filter by crop residue name"),
    location: Optional[str] = Query(None, description="Filter by delivery location"),
    status: Optional[RequirementStatus] = Query(RequirementStatus.OPEN, description="Filter by status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Retrieve public buyer requirements for farmers and aggregators to explore demand."""
    query = db.query(BuyerRequirement)
    if status:
        query = query.filter(BuyerRequirement.status == status)
    if material:
        query = query.filter(BuyerRequirement.material_name.ilike(f"%{material}%"))
    if location:
        query = query.filter(BuyerRequirement.delivery_location.ilike(f"%{location}%"))
    
    return query.order_by(desc(BuyerRequirement.created_at)).offset(skip).limit(limit).all()


@router.get("/my", response_model=List[BuyerRequirementResponse])
def get_my_requirements(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.BUYER))
):
    """Get all requirements published by the logged-in industrial buyer."""
    return db.query(BuyerRequirement).filter(
        BuyerRequirement.buyer_id == current_user.id
    ).order_by(desc(BuyerRequirement.created_at)).all()


@router.get("/{requirement_id}", response_model=BuyerRequirementResponse)
def get_requirement(requirement_id: int, db: Session = Depends(get_db)):
    """Fetch details of a single buyer requirement."""
    requirement = db.query(BuyerRequirement).filter(BuyerRequirement.id == requirement_id).first()
    if not requirement:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Requirement not found")
    return requirement


@router.patch("/{requirement_id}", response_model=BuyerRequirementResponse)
def update_requirement(
    requirement_id: int,
    data: BuyerRequirementUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update requirement details or status. Only the buyer who created it or admin is authorized."""
    requirement = db.query(BuyerRequirement).filter(BuyerRequirement.id == requirement_id).first()
    if not requirement:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Requirement not found")
    
    if requirement.buyer_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to edit this requirement")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(requirement, field, value)
    
    db.commit()
    db.refresh(requirement)
    return requirement


@router.delete("/{requirement_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_requirement(
    requirement_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cancel or remove a buyer requirement."""
    requirement = db.query(BuyerRequirement).filter(BuyerRequirement.id == requirement_id).first()
    if not requirement:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Requirement not found")
    
    if requirement.buyer_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this requirement")

    db.delete(requirement)
    db.commit()
    return None


@router.get("/{requirement_id}/matching-listings", response_model=List[WasteListingResponse])
def get_matching_listings_for_requirement(
    requirement_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Find available farmer residue listings that match this buyer requirement's material."""
    requirement = db.query(BuyerRequirement).filter(BuyerRequirement.id == requirement_id).first()
    if not requirement:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Requirement not found")

    # Match available listings with the same material
    query = db.query(WasteListing).filter(
        WasteListing.status == ListingStatus.AVAILABLE,
        WasteListing.material_name.ilike(f"%{requirement.material_name}%"),
        WasteListing.available_quantity > 0
    )

    # Optional price filter if target_price_max is set
    if requirement.target_price_max:
        query = query.filter(WasteListing.price_per_unit <= requirement.target_price_max * 1.15)  # within 15% tolerance

    return query.order_by(WasteListing.price_per_unit.asc()).all()
