from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.requirement import BuyerRequirement, RequirementStatus
from app.models.listing import WasteListing, ListingStatus
from app.services.matching import calculate_match_score
from app.routers.deps import get_current_user
from app.models.user import User, UserRole

router = APIRouter(prefix="/matches", tags=["Matching Engine"])


@router.get("/requirements/{requirement_id}", response_model=List[Dict[str, Any]])
def get_ranked_matches_for_requirement(
    requirement_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Week 5: Smart Matching Engine
    Returns all suitable available farmer listings ranked by rule-based matching score
    along with transparent explainable score breakdown.
    Excludes cancelled or fulfilled requirements from active matching.
    """
    req = db.query(BuyerRequirement).filter(BuyerRequirement.id == requirement_id).first()
    if not req:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Buyer requirement not found")

    # Only the requirement owner or an admin may view ranked matches
    if req.buyer_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access matches for this requirement")

    # Exclude closed or cancelled requirements from active matching
    if req.status in [RequirementStatus.CANCELLED, RequirementStatus.FULFILLED]:
        return []

    # Fetch all available listings with stock
    listings = db.query(WasteListing).filter(
        WasteListing.status == ListingStatus.AVAILABLE,
        WasteListing.available_quantity > 0
    ).all()

    ranked = []
    for l in listings:
        match_result = calculate_match_score(req, l)
        if match_result["is_compatible"] and match_result["total_score"] > 0:
            farmer_name = l.farmer.full_name if l.farmer else f"Farmer #{l.farmer_id}"
            ranked.append({
                "listing_id": l.id,
                "farmer_id": l.farmer_id,
                "farmer_name": farmer_name,
                "material_name": l.material_name,
                "available_quantity": l.available_quantity,
                "unit": l.unit,
                "price_per_unit": l.price_per_unit,
                "location_name": l.location_name,
                "storage_type": l.storage_type,
                "moisture_condition": l.moisture_condition,
                "score": match_result["total_score"],
                "reason": match_result["reason"],
                "breakdown": match_result["breakdown"],
            })

    # Sort descending by match score
    ranked.sort(key=lambda x: x["score"], reverse=True)
    return ranked
