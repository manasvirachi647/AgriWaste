from typing import Dict, Any, List
from app.models.listing import WasteListing, ListingStatus
from app.models.requirement import BuyerRequirement


def calculate_match_score(
    requirement: BuyerRequirement,
    listing: WasteListing
) -> Dict[str, Any]:
    """
    Calculates rule-based matching score (0 to 100) and breakdown
    based on Section 6.4 of the Master Blueprint:
    - Material compatibility: 30% (Hard filter)
    - Quantity suitability: 20%
    - Distance / Location: 20%
    - Price compatibility: 15%
    - Availability timing: 10%
    - Quality & storage: 5%
    """
    # 1. Material compatibility (Hard filter)
    req_mat = requirement.material_name.strip().lower()
    list_mat = listing.material_name.strip().lower()
    
    if req_mat not in list_mat and list_mat not in req_mat:
        return {
            "is_compatible": False,
            "total_score": 0.0,
            "reason": f"Material mismatch: required '{requirement.material_name}' vs listing '{listing.material_name}'",
            "breakdown": {}
        }
    
    material_score = 30.0

    # 2. Quantity suitability (20%)
    avail_qty = listing.available_quantity
    req_qty = max(0.1, requirement.required_quantity - (requirement.fulfilled_quantity or 0.0))
    
    if avail_qty >= req_qty:
        quantity_score = 20.0
        qty_note = "Single farmer can fully fulfill the requirement"
    else:
        # Partial contribution ratio
        ratio = min(1.0, avail_qty / req_qty)
        quantity_score = round(ratio * 20.0, 1)
        qty_note = f"Farmer can contribute {avail_qty} {listing.unit} ({round(ratio*100)}% of remaining demand)"

    # 3. Location / Distance suitability (20%)
    req_loc = requirement.delivery_location.lower()
    list_loc = listing.location_name.lower()
    
    # Simple district/city text matching heuristic for prototype
    common_tokens = set(req_loc.replace(',', ' ').split()) & set(list_loc.replace(',', ' ').split())
    if len(common_tokens) >= 2:
        distance_score = 20.0
        dist_note = "Local supplier in the same district/city"
    elif len(common_tokens) >= 1:
        distance_score = 15.0
        dist_note = "Regional supplier within reasonable transport range"
    else:
        distance_score = 10.0
        dist_note = "Inter-district pickup (standard transport rates apply)"

    # 4. Price compatibility (15%)
    price = listing.price_per_unit
    max_price = requirement.target_price_max
    min_price = requirement.target_price_min

    if max_price:
        if price <= max_price:
            price_score = 15.0
            price_note = f"Rate (₹{price}) is within buyer budget (Max ₹{max_price})"
        elif price <= max_price * 1.15:
            price_score = 8.0
            price_note = f"Rate (₹{price}) is slightly above budget (Max ₹{max_price})"
        else:
            price_score = 2.0
            price_note = f"Rate (₹{price}) exceeds target budget"
    else:
        price_score = 12.0
        price_note = f"Fair market rate offered: ₹{price}/{listing.unit}"

    # 5. Availability (10%)
    availability_score = 10.0 if listing.status == ListingStatus.AVAILABLE else 0.0
    avail_note = "Immediate stock available for pickup"

    # 6. Quality & Storage (5%)
    storage = (listing.storage_type or "").lower()
    if "covered" in storage or "silo" in storage:
        quality_score = 5.0
        qual_note = "High quality: stored in covered dry shed/silo"
    elif "baled" in storage:
        quality_score = 4.0
        qual_note = "Standard quality: baled and stacked"
    else:
        quality_score = 3.0
        qual_note = "Standard field storage"

    total = round(material_score + quantity_score + distance_score + price_score + availability_score + quality_score, 1)

    return {
        "is_compatible": True,
        "total_score": total,
        "reason": f"Strong match for {listing.material_name} ({total}/100)",
        "breakdown": {
            "material_score": material_score,
            "quantity_score": quantity_score,
            "quantity_note": qty_note,
            "distance_score": distance_score,
            "distance_note": dist_note,
            "price_score": price_score,
            "price_note": price_note,
            "availability_score": availability_score,
            "quality_score": quality_score,
            "quality_note": qual_note,
        }
    }
