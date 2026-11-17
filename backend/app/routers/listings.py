from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import get_db
from app.models.user import User, UserRole
from app.models.listing import WasteListing, ListingStatus
from app.models.requirement import BuyerRequirement, RequirementStatus
from app.schemas.listing import WasteListingCreate, WasteListingUpdate, WasteListingResponse
from app.schemas.requirement import BuyerRequirementResponse
from app.routers.deps import get_current_user, require_role

router = APIRouter(prefix="/listings", tags=["Farmer Listings"])


@router.post("", response_model=WasteListingResponse, status_code=status.HTTP_201_CREATED)
def create_listing(
    data: WasteListingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.FARMER))
):
    """Create a new residue listing. Farmer ID is safely taken from authenticated session."""
    listing = WasteListing(
        farmer_id=current_user.id,
        material_name=data.material_name.strip(),
        estimated_quantity=data.estimated_quantity,
        available_quantity=data.estimated_quantity,  # initial available equals estimated
        unit=data.unit,
        price_per_unit=data.price_per_unit,
        location_name=data.location_name.strip(),
        latitude=data.latitude,
        longitude=data.longitude,
        available_from=data.available_from,
        available_until=data.available_until,
        storage_type=data.storage_type,
        moisture_condition=data.moisture_condition,
        quality_notes=data.quality_notes,
        photo_urls=data.photo_urls,
        status=ListingStatus.AVAILABLE,
    )
    db.add(listing)
    db.commit()
    db.refresh(listing)
    return listing


@router.get("", response_model=List[WasteListingResponse])
def get_all_listings(
    material: Optional[str] = Query(None, description="Filter by crop/material name"),
    location: Optional[str] = Query(None, description="Filter by location name"),
    status: Optional[ListingStatus] = Query(ListingStatus.AVAILABLE, description="Filter by status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Retrieve public agricultural waste listings for buyers and transporters to browse."""
    query = db.query(WasteListing)
    if status:
        query = query.filter(WasteListing.status == status)
    if material:
        query = query.filter(WasteListing.material_name.ilike(f"%{material}%"))
    if location:
        query = query.filter(WasteListing.location_name.ilike(f"%{location}%"))
    
    return query.order_by(desc(WasteListing.created_at)).offset(skip).limit(limit).all()


@router.get("/my", response_model=List[WasteListingResponse])
def get_my_listings(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.FARMER))
):
    """Get all listings created by the logged-in farmer."""
    return db.query(WasteListing).filter(
        WasteListing.farmer_id == current_user.id
    ).order_by(desc(WasteListing.created_at)).all()


@router.get("/{listing_id}", response_model=WasteListingResponse)
def get_listing(listing_id: int, db: Session = Depends(get_db)):
    """Fetch details of a single residue listing."""
    listing = db.query(WasteListing).filter(WasteListing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found")
    return listing


@router.patch("/{listing_id}", response_model=WasteListingResponse)
def update_listing(
    listing_id: int,
    data: WasteListingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a listing. Only the farmer who created it (or admin) is permitted."""
    listing = db.query(WasteListing).filter(WasteListing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found")
    
    if listing.farmer_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to edit this listing")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(listing, field, value)
    
    db.commit()
    db.refresh(listing)
    return listing


@router.delete("/{listing_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_listing(
    listing_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cancel or remove a listing."""
    listing = db.query(WasteListing).filter(WasteListing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found")
    
    if listing.farmer_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this listing")

    db.delete(listing)
    db.commit()
    return None


@router.get("/{listing_id}/matching-requirements", response_model=List[BuyerRequirementResponse])
def get_matching_requirements_for_listing(
    listing_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Find open buyer requirements seeking the crop material offered in this listing."""
    listing = db.query(WasteListing).filter(WasteListing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found")

    query = db.query(BuyerRequirement).filter(
        BuyerRequirement.status == RequirementStatus.OPEN,
        BuyerRequirement.material_name.ilike(f"%{listing.material_name}%")
    )

    return query.order_by(desc(BuyerRequirement.required_quantity)).all()
