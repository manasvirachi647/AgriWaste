import os
import sys
from pathlib import Path

# Add backend directory to sys.path
BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

# Use test SQLite database
TEST_DB = BACKEND_DIR / "test_phase3_4.db"
if TEST_DB.exists():
    try:
        TEST_DB.unlink()
    except Exception:
        pass

os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB}"

from fastapi import HTTPException
from app.database import Base, engine, SessionLocal
from app.models.user import User, UserRole
from app.models.listing import WasteListing, ListingStatus
from app.models.requirement import BuyerRequirement, RequirementStatus
from app.schemas.auth import RegisterRequest
from app.schemas.listing import WasteListingCreate, WasteListingUpdate
from app.schemas.requirement import BuyerRequirementCreate, BuyerRequirementUpdate
from app.routers import auth, listings, requirements
from app.routers.deps import require_role


def run_phase3_and_4_tests():
    print("=======================================================", flush=True)
    print(" AGRIWASTE EXCHANGE: PHASE 3 & 4 VERIFICATION SUITE   ", flush=True)
    print(" (Phase 3: Farmer Module & Phase 4: Buyer Module)     ", flush=True)
    print("=======================================================", flush=True)

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Step 1: Register Farmer
        print("\n[Step 1] Registering Farmer User...", flush=True)
        farmer_req = RegisterRequest(
            username="kisan_ramesh",
            email="ramesh.farmer@agriwaste.in",
            password="KisanPassword123!",
            full_name="Ramesh Patel",
            phone_number="+919876543210",
            role=UserRole.FARMER,
            farm_village="Sanand",
            district="Ahmedabad",
        )
        auth_farmer = auth.register(farmer_req, db)
        farmer_user = db.query(User).filter(User.username == "kisan_ramesh").first()
        assert farmer_user is not None
        print(f" Farmer registered: {farmer_user.full_name} (ID: {farmer_user.id})", flush=True)

        # Step 2: Register Buyer
        print("\n[Step 2] Registering Industrial Buyer User...", flush=True)
        buyer_req = RegisterRequest(
            username="green_biopower",
            email="procure@greenbiopower.com",
            password="IndustryPassword456!",
            full_name="Vikram Mehta",
            phone_number="+919822334455",
            role=UserRole.BUYER,
            company_name="Green BioPower Industries Ltd",
            industry_type="Biomass Cogeneration & Energy",
        )
        auth_buyer = auth.register(buyer_req, db)
        buyer_user = db.query(User).filter(User.username == "green_biopower").first()
        assert buyer_user is not None
        print(f" Industrial Buyer registered: {buyer_user.buyer_profile.company_name} (ID: {buyer_user.id})", flush=True)

        # Step 3: Farmer Creates Crop Residue Listings (Phase 3)
        print("\n[Step 3] Farmer Creates Multiple Crop Residue Listings...", flush=True)
        listing1_in = WasteListingCreate(
            material_name="Rice Husk",
            estimated_quantity=6.0,
            unit="tonnes",
            price_per_unit=2400.0,
            location_name="Sanand, Ahmedabad, Gujarat",
            storage_type="Dry covered shed",
            moisture_condition="Dry (< 12%)",
            quality_notes="Clean dry golden rice husk harvest, bagged in 50kg bags",
        )
        listing1 = listings.create_listing(listing1_in, db, farmer_user)
        assert listing1.id is not None
        assert listing1.available_quantity == 6.0
        assert listing1.status == ListingStatus.AVAILABLE
        print(f" Created Listing #1: {listing1.material_name} - {listing1.available_quantity} {listing1.unit} at Rs.{listing1.price_per_unit}", flush=True)

        listing2_in = WasteListingCreate(
            material_name="Wheat Straw",
            estimated_quantity=10.0,
            unit="tonnes",
            price_per_unit=1800.0,
            location_name="Bavla, Ahmedabad, Gujarat",
            storage_type="Baled & Stacked",
            moisture_condition="Medium (14%)",
            quality_notes="Chopped and baled wheat straw ready for tractor pickup",
        )
        listing2 = listings.create_listing(listing2_in, db, farmer_user)
        assert listing2.id is not None
        print(f" Created Listing #2: {listing2.material_name} - {listing2.available_quantity} {listing2.unit} at Rs.{listing2.price_per_unit}", flush=True)

        # Step 4: Farmer Personal Listings Query (Phase 3)
        print("\n[Step 4] Testing Farmer Personal Listings Query...", flush=True)
        my_listings = listings.get_my_listings(db, farmer_user)
        assert len(my_listings) == 2
        print(f" Farmer successfully retrieved {len(my_listings)} personal residue listings.", flush=True)

        # Step 5: Farmer Updates Listing (Phase 3)
        print("\n[Step 5] Farmer Updates Price & Storage Conditions...", flush=True)
        update_data = WasteListingUpdate(price_per_unit=2300.0, storage_type="Air-tight shed")
        updated_listing = listings.update_listing(listing1.id, update_data, db, farmer_user)
        assert updated_listing.price_per_unit == 2300.0
        assert updated_listing.storage_type == "Air-tight shed"
        print(f" Listing #1 updated successfully: New rate = Rs.{updated_listing.price_per_unit}", flush=True)

        # Step 6: Buyer Publishes Biomass Requirements (Phase 4)
        print("\n[Step 6] Buyer Publishes Industrial Biomass Requirements...", flush=True)
        req1_in = BuyerRequirementCreate(
            material_name="Rice Husk",
            required_quantity=15.0,
            unit="tonnes",
            target_price_min=2000.0,
            target_price_max=2500.0,
            delivery_location="Sanand Industrial Estate, Ahmedabad",
            quality_specifications="Moisture < 13%, no plastic or stones",
        )
        req1 = requirements.create_requirement(req1_in, db, buyer_user)
        assert req1.id is not None
        assert req1.buyer_id == buyer_user.id
        assert req1.required_quantity == 15.0
        assert req1.status == RequirementStatus.OPEN
        print(f" Created Requirement #1: {req1.material_name} - {req1.required_quantity} {req1.unit} for plant delivery", flush=True)

        req2_in = BuyerRequirementCreate(
            material_name="Wheat Straw",
            required_quantity=25.0,
            unit="tonnes",
            target_price_min=1500.0,
            target_price_max=2000.0,
            delivery_location="Viramgam Plant, Ahmedabad",
            quality_specifications="Baled form preferred",
        )
        req2 = requirements.create_requirement(req2_in, db, buyer_user)
        assert req2.id is not None
        print(f" Created Requirement #2: {req2.material_name} - {req2.required_quantity} {req2.unit}", flush=True)

        # Step 7: Buyer Personal Requirements Query (Phase 4)
        print("\n[Step 7] Testing Buyer Personal Requirements Query...", flush=True)
        my_reqs = requirements.get_my_requirements(db, buyer_user)
        assert len(my_reqs) == 2
        print(f" Buyer successfully retrieved {len(my_reqs)} published requirements.", flush=True)

        # Step 8: Strict Role-Based Access Control (RBAC)
        print("\n[Step 8] Testing Role-Based Access Control Isolation...", flush=True)
        # Farmer checker should block buyer from adding farmer listing
        farmer_check = require_role(UserRole.FARMER)
        try:
            farmer_check(buyer_user)
            assert False, "Buyer must not pass Farmer role check"
        except HTTPException as e:
            assert e.status_code == 403
            print(" RBAC: Buyer blocked from farmer endpoints (HTTP 403)", flush=True)

        # Buyer checker should block farmer from creating buyer requirement
        buyer_check = require_role(UserRole.BUYER)
        try:
            buyer_check(farmer_user)
            assert False, "Farmer must not pass Buyer role check"
        except HTTPException as e:
            assert e.status_code == 403
            print(" RBAC: Farmer blocked from buyer endpoints (HTTP 403)", flush=True)

        # Step 9: Matching Suppliers Discovery for Buyer (Phase 4 -> Phase 3 integration)
        print("\n[Step 9] Buyer Discovers Available Matching Farmer Listings...", flush=True)
        matching_listings = requirements.get_matching_listings_for_requirement(req1.id, db, buyer_user)
        assert len(matching_listings) >= 1
        assert matching_listings[0].material_name == "Rice Husk"
        print(f" Found {len(matching_listings)} matching supplier listing(s) for Requirement #1 ({req1.material_name}):", flush=True)
        for m in matching_listings:
            print(f"   -> Listing #{m.id}: {m.available_quantity} {m.unit} at Rs.{m.price_per_unit}/{m.unit} from {m.location_name}", flush=True)

        # Step 10: Matching Demands Discovery for Farmer (Phase 3 -> Phase 4 integration)
        print("\n[Step 10] Farmer Discovers Matching Buyer Demands...", flush=True)
        matching_demands = listings.get_matching_requirements_for_listing(listing1.id, db, farmer_user)
        assert len(matching_demands) >= 1
        assert matching_demands[0].material_name == "Rice Husk"
        print(f" Found {len(matching_demands)} open demand(s) seeking {listing1.material_name}:", flush=True)
        for d in matching_demands:
            print(f"   -> Requirement #{d.id}: {d.required_quantity} {d.unit} delivering to {d.delivery_location}", flush=True)

        # Step 11: Buyer Closes/Cancels a Requirement
        print("\n[Step 11] Testing Buyer Requirement Status Lifecycle...", flush=True)
        req_update = BuyerRequirementUpdate(status=RequirementStatus.CANCELLED)
        closed_req = requirements.update_requirement(req2.id, req_update, db, buyer_user)
        assert closed_req.status == RequirementStatus.CANCELLED
        print(f" Requirement #{closed_req.id} status successfully transitioned to '{closed_req.status.value}'.", flush=True)

        # Step 12: Ownership Protection Check
        print("\n[Step 12] Testing Unauthorized Ownership Modification Protection...", flush=True)
        # Farmer tries to update buyer's requirement -> must be HTTP 403
        try:
            requirements.update_requirement(req1.id, req_update, db, farmer_user)
            assert False, "Farmer should not be able to modify buyer's requirement"
        except HTTPException as e:
            assert e.status_code == 403
            print(f" Unauthorized edit blocked with HTTP 403: {e.detail}", flush=True)

        print("\n=======================================================", flush=True)
        print(" ALL PHASE 3 & PHASE 4 VERIFICATION TESTS PASSED 100%! ", flush=True)
        print("=======================================================", flush=True)

    finally:
        db.close()
        if TEST_DB.exists():
            try:
                TEST_DB.unlink()
            except Exception:
                pass


if __name__ == "__main__":
    run_phase3_and_4_tests()
