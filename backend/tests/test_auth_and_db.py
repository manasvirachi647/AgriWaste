import os
import sys
from pathlib import Path

# Add backend directory to sys.path
BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

# Use a test SQLite database
TEST_DB = BACKEND_DIR / "test_agriwaste.db"
if TEST_DB.exists():
    try:
        TEST_DB.unlink()
    except Exception:
        pass

os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB}"

from fastapi import HTTPException
from app.database import Base, engine, SessionLocal
from app.models.user import User, UserRole, FarmerProfile, BuyerProfile, AggregatorProfile
from app.models.listing import WasteListing, ListingStatus
from app.schemas.auth import RegisterRequest, LoginRequest
from app.schemas.listing import WasteListingCreate
from app.routers import auth, listings
from app.core.security import verify_password, decode_access_token


def run_full_suite():
    print("==================================================", flush=True)
    print(" AGRIWASTE EXCHANGE: WEEK 1 & 2 VERIFICATION TEST ", flush=True)
    print("==================================================", flush=True)

    # 1. Initialize clean schema
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Step 1: Register Farmer
        print("\n[Step 1] Registering Farmer User...", flush=True)
        farmer_req = RegisterRequest(
            username="ramesh_farmer",
            email="ramesh@example.com",
            password="StrongPassword123!",
            full_name="Ramesh Patel",
            phone_number="+919876543210",
            role=UserRole.FARMER,
            farm_village="Sanand",
            district="Ahmedabad",
        )
        res_farmer = auth.register(farmer_req, db)
        assert res_farmer.user.role == UserRole.FARMER
        assert res_farmer.user.farmer_profile.farm_village == "Sanand"
        assert res_farmer.access_token is not None
        farmer_token = res_farmer.access_token
        farmer_user = db.query(User).filter(User.username == "ramesh_farmer").first()
        assert farmer_user is not None
        assert verify_password("StrongPassword123!", farmer_user.hashed_password)
        print(f" Farmer '{farmer_user.full_name}' registered successfully with ID: {farmer_user.id}", flush=True)

        # Step 2: Register Industrial Buyer
        print("\n[Step 2] Registering Industrial Buyer...", flush=True)
        buyer_req = RegisterRequest(
            username="gujarat_biopower",
            email="procure@gujaratbiopower.com",
            password="IndustryPass456!",
            full_name="Vikram Mehta",
            phone_number="+919811223344",
            role=UserRole.BUYER,
            company_name="Gujarat BioPower Industries Ltd",
            industry_type="Biomass Cogeneration & Power",
        )
        res_buyer = auth.register(buyer_req, db)
        assert res_buyer.user.role == UserRole.BUYER
        assert res_buyer.user.buyer_profile.company_name == "Gujarat BioPower Industries Ltd"
        buyer_user = db.query(User).filter(User.username == "gujarat_biopower").first()
        print(f" Buyer '{buyer_user.buyer_profile.company_name}' registered successfully with ID: {buyer_user.id}", flush=True)

        # Step 3: Register Aggregator / Transporter
        print("\n[Step 3] Registering Transporter / Aggregator...", flush=True)
        agg_req = RegisterRequest(
            username="kisan_transport",
            email="logistics@kisantransport.in",
            password="TruckFleet789!",
            full_name="Harpreet Singh",
            phone_number="+919988776655",
            role=UserRole.AGGREGATOR,
            vehicle_type="10-Wheeler Heavy Truck (15 Tonnes)",
            district="Ahmedabad",
        )
        res_agg = auth.register(agg_req, db)
        assert res_agg.user.role == UserRole.AGGREGATOR
        assert res_agg.user.aggregator_profile.vehicle_type == "10-Wheeler Heavy Truck (15 Tonnes)"
        print(" Transporter registered with vehicle profile successfully.", flush=True)

        # Step 4: Duplicate Registration Prevention
        print("\n[Step 4] Testing Duplicate Prevention...", flush=True)
        try:
            auth.register(farmer_req, db)
            assert False, "Should have raised HTTPException 400 for duplicate username"
        except HTTPException as e:
            assert e.status_code == 400
            print(" Duplicate username properly blocked with HTTP 400:", e.detail, flush=True)

        # Step 5: Login Flow & Token Validation
        print("\n[Step 5] Testing Login Flow & JWT Verification...", flush=True)
        login_req = LoginRequest(username_or_email="ramesh_farmer", password="StrongPassword123!")
        login_res = auth.login(login_req, db)
        assert login_res.access_token is not None
        decoded = decode_access_token(login_res.access_token)
        assert decoded is not None
        assert decoded["sub"] == str(farmer_user.id)
        assert decoded["role"] == "farmer"
        print(" Login succeeded! JWT token issued and decoded successfully. Role:", decoded["role"], flush=True)

        # Step 6: Invalid Credentials Test
        print("\n[Step 6] Testing Invalid Password Handling...", flush=True)
        bad_login = LoginRequest(username_or_email="ramesh_farmer", password="WrongPassword!")
        try:
            auth.login(bad_login, db)
            assert False, "Should have failed login with wrong password"
        except HTTPException as e:
            assert e.status_code == 401
            print(" Invalid password rejected with HTTP 401:", e.detail, flush=True)

        # Step 7: Farmer Creates Residue Listing
        print("\n[Step 7] Farmer Creates Residue Listing...", flush=True)
        listing_input = WasteListingCreate(
            material_name="Rice Husk",
            estimated_quantity=4.5,
            unit="tonnes",
            price_per_unit=2500.0,
            location_name="Sanand, Ahmedabad, Gujarat",
            storage_type="Covered dry shed",
            moisture_condition="Dry (< 12%)",
            quality_notes="Freshly harvested rice husk, free from stones and contamination.",
        )
        created_listing = listings.create_listing(
            data=listing_input,
            db=db,
            current_user=farmer_user
        )
        assert created_listing.id is not None
        assert created_listing.farmer_id == farmer_user.id
        assert created_listing.material_name == "Rice Husk"
        assert created_listing.available_quantity == 4.5
        assert created_listing.status == ListingStatus.AVAILABLE
        print(f" Listing #{created_listing.id} created: {created_listing.material_name} - {created_listing.available_quantity} {created_listing.unit} at Rs.{created_listing.price_per_unit}/{created_listing.unit}", flush=True)

        # Step 8: RBAC Enforcement
        print("\n[Step 8] Testing Role-Based Access Control (RBAC)...", flush=True)
        from app.routers.deps import require_role
        farmer_checker = require_role(UserRole.FARMER)
        try:
            farmer_checker(buyer_user)
            assert False, "Buyer must not pass farmer role check"
        except HTTPException as e:
            assert e.status_code == 403
            print(" RBAC successfully prevented Buyer from accessing Farmer-only operation (HTTP 403):", e.detail, flush=True)

        # Step 9: Query and Filter Listings
        print("\n[Step 9] Testing Residue Listings Filtering...", flush=True)
        all_listings = listings.get_all_listings(
            material="Rice",
            location="Sanand",
            status=ListingStatus.AVAILABLE,
            skip=0,
            limit=10,
            db=db
        )
        assert len(all_listings) == 1
        assert all_listings[0].material_name == "Rice Husk"
        print(f" Successfully found {len(all_listings)} listing matching material='Rice' and location='Sanand'", flush=True)

        # Step 10: Farmer's Own Listings
        print("\n[Step 10] Testing Farmer's Personal Listings Query...", flush=True)
        my_listings = listings.get_my_listings(db=db, current_user=farmer_user)
        assert len(my_listings) == 1
        assert my_listings[0].id == created_listing.id
        print(" Farmer personal listings query correctly returned 1 listing.", flush=True)

        print("\n==================================================", flush=True)
        print(" SUCCESS: ALL WEEK 1 & 2 MILESTONES VERIFIED 100% ", flush=True)
        print("==================================================", flush=True)

    finally:
        db.close()
        if TEST_DB.exists():
            try:
                TEST_DB.unlink()
            except Exception:
                pass


if __name__ == "__main__":
    run_full_suite()
