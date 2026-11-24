import os
import sys
from pathlib import Path

# Add backend directory to sys.path
BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

# Use test SQLite database
TEST_DB = BACKEND_DIR / "test_full_platform.db"
if TEST_DB.exists():
    try:
        TEST_DB.unlink()
    except Exception:
        pass

os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB}"

from app.database import Base, engine, SessionLocal
from app.models.user import User, UserRole
from app.models.listing import WasteListing, ListingStatus
from app.models.requirement import BuyerRequirement, RequirementStatus
from app.models.order import Order, OrderStatus
from app.models.transport import TransportJob, TransportStatus
from app.models.issue import IssueCategory, IssueStatus
from app.schemas.auth import RegisterRequest
from app.schemas.listing import WasteListingCreate
from app.schemas.requirement import BuyerRequirementCreate
from app.schemas.order import OrderCreateAllocationRequest, OrderContributionItem
from app.schemas.transport import TransportStatusUpdate
from app.schemas.issue import IssueCreate, IssueResolve
from app.routers import auth, listings, requirements, matches, orders, transport, issues, admin


def run_full_platform_verification():
    print("==================================================================", flush=True)
    print(" AGRIWASTE EXCHANGE: COMPLETE WEEKS 1 TO 8 VERIFICATION TEST     ", flush=True)
    print("==================================================================", flush=True)

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Step 1: Register 3 Farmers, 1 Buyer, 1 Transporter, 1 Admin
        print("\n[Step 1] Registering Platform Users...", flush=True)
        # Farmer A
        auth.register(RegisterRequest(
            username="farmer_a", email="fa@farm.in", password="Pass123!Safe",
            full_name="Farmer A (Ramesh)", role=UserRole.FARMER, farm_village="Sanand", district="Ahmedabad"
        ), db)
        farmer_a = db.query(User).filter(User.username == "farmer_a").first()

        # Farmer B
        auth.register(RegisterRequest(
            username="farmer_b", email="fb@farm.in", password="Pass123!Safe",
            full_name="Farmer B (Suresh)", role=UserRole.FARMER, farm_village="Bavla", district="Ahmedabad"
        ), db)
        farmer_b = db.query(User).filter(User.username == "farmer_b").first()

        # Farmer C
        auth.register(RegisterRequest(
            username="farmer_c", email="fc@farm.in", password="Pass123!Safe",
            full_name="Farmer C (Mahesh)", role=UserRole.FARMER, farm_village="Dholka", district="Ahmedabad"
        ), db)
        farmer_c = db.query(User).filter(User.username == "farmer_c").first()

        # Industrial Buyer
        auth.register(RegisterRequest(
            username="gujarat_biomass", email="buy@biomass.com", password="Pass123!Safe",
            full_name="Vikram Mehta", role=UserRole.BUYER, company_name="Gujarat BioPower Ltd", industry_type="Energy"
        ), db)
        buyer = db.query(User).filter(User.username == "gujarat_biomass").first()

        # Transporter
        auth.register(RegisterRequest(
            username="kisan_trucks", email="truck@fleet.in", password="Pass123!Safe",
            full_name="Harpreet Singh", role=UserRole.AGGREGATOR, vehicle_type="10T Truck", district="Ahmedabad"
        ), db)
        transporter = db.query(User).filter(User.username == "kisan_trucks").first()

        # Admin (system-provisioned directly; public self-registration is blocked)
        from app.core.security import hash_password
        admin_user = User(
            username="platform_admin", email="admin@agriwaste.in",
            hashed_password=hash_password("Pass123!Safe"),
            full_name="System Admin", role=UserRole.ADMIN, is_active=True
        )
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)

        print(" Users created: 3 Farmers, 1 Buyer, 1 Transporter, 1 Admin.", flush=True)

        # Step 2: Demonstration Scenario (Section 18 of Master Blueprint):
        # Farmer A lists 2T Rice Husk @ 2400
        # Farmer B lists 3T Rice Husk @ 2350
        # Farmer C lists 5T Rice Husk @ 2300
        print("\n[Step 2] Farmers Post Crop Residue Listings...", flush=True)
        l_a = listings.create_listing(WasteListingCreate(
            material_name="Rice Husk", estimated_quantity=2.0, unit="tonnes",
            price_per_unit=2400.0, location_name="Sanand, Ahmedabad", storage_type="Covered shed"
        ), db, farmer_a)

        l_b = listings.create_listing(WasteListingCreate(
            material_name="Rice Husk", estimated_quantity=3.0, unit="tonnes",
            price_per_unit=2350.0, location_name="Bavla, Ahmedabad", storage_type="Baled"
        ), db, farmer_b)

        l_c = listings.create_listing(WasteListingCreate(
            material_name="Rice Husk", estimated_quantity=5.0, unit="tonnes",
            price_per_unit=2300.0, location_name="Dholka, Ahmedabad", storage_type="Covered shed"
        ), db, farmer_c)

        print(f" Listings created: #{l_a.id} (2T), #{l_b.id} (3T), #{l_c.id} (5T)", flush=True)

        # Step 3: Industrial Buyer Posts 10T Rice Husk Requirement
        print("\n[Step 3] Buyer Publishes Requirement (10 Tonnes Needed)...", flush=True)
        req = requirements.create_requirement(BuyerRequirementCreate(
            material_name="Rice Husk", required_quantity=10.0, unit="tonnes",
            target_price_max=2500.0, delivery_location="Sanand Industrial Plant, Ahmedabad"
        ), db, buyer)
        assert req.id is not None
        assert req.status == RequirementStatus.OPEN
        print(f" Requirement #{req.id} created: {req.required_quantity} {req.unit} {req.material_name}", flush=True)

        # Step 4: Smart Matching Engine (Week 5)
        print("\n[Step 4] Running Smart Matching Engine...", flush=True)
        scored_matches = matches.get_ranked_matches_for_requirement(req.id, db, buyer)
        assert len(scored_matches) == 3
        print(f" Found {len(scored_matches)} ranked compatible matches:")
        for sm in scored_matches:
            print(f"   -> Match #{sm['listing_id']}: Score {sm['score']}/100 | {sm['reason']}")

        # Step 5: Multi-Farmer Order Allocation (Core USP: 2T + 3T + 5T = 10T)
        print("\n[Step 5] Multi-Farmer Order Allocation (2 + 3 + 5 = 10 Tonnes)...", flush=True)
        order_req = OrderCreateAllocationRequest(
            requirement_id=req.id,
            contributions=[
                OrderContributionItem(listing_id=l_a.id, allocated_quantity=2.0),
                OrderContributionItem(listing_id=l_b.id, allocated_quantity=3.0),
                OrderContributionItem(listing_id=l_c.id, allocated_quantity=5.0),
            ],
            delivery_address="Sanand GIDC Biofuel Plant, Ahmedabad"
        )
        created_order = orders.create_order(order_req, db, buyer)
        assert created_order.id is not None
        assert created_order.total_quantity == 10.0
        assert len(created_order.items) == 3
        print(f" Order #{created_order.id} confirmed! Total Quantity: {created_order.total_quantity} tonnes | Total Amount: Rs.{created_order.total_amount}", flush=True)

        # Step 6: Verify Database Inventory Reservation & Requirement Fulfillment
        print("\n[Step 6] Verifying Inventory Reservation & Locks...", flush=True)
        db.refresh(l_a)
        db.refresh(l_b)
        db.refresh(l_c)
        db.refresh(req)
        assert l_a.available_quantity == 0.0 and l_a.status == ListingStatus.RESERVED
        assert l_b.available_quantity == 0.0 and l_b.status == ListingStatus.RESERVED
        assert l_c.available_quantity == 0.0 and l_c.status == ListingStatus.RESERVED
        assert req.status == RequirementStatus.FULFILLED
        print(" All 3 listing stocks reserved safely to 0 available. Requirement marked FULFILLED.", flush=True)

        # Step 7: Transporter Workflow (Week 6)
        print("\n[Step 7] Transporter Claims Job & Updates Route Progress...", flush=True)
        jobs = transport.get_transport_jobs(db, transporter)
        assert len(jobs) >= 1
        job = jobs[0]
        print(f" Transport Job #{job.id} found: Est Distance {job.estimated_distance_km} km | Est Payout Rs.{job.estimated_cost}", flush=True)
        
        claimed = transport.claim_transport_job(job.id, db, transporter)
        assert claimed.aggregator_id == transporter.id

        delivered = transport.update_transport_status(job.id, TransportStatusUpdate(
            status=TransportStatus.DELIVERED, notes="Delivered 10 tonnes to plant weighbridge"
        ), db, transporter)
        assert delivered.status == TransportStatus.DELIVERED
        print(" Transport status advanced to DELIVERED.", flush=True)

        # Step 8: Issue Reporting & Admin Resolution (Week 7)
        print("\n[Step 8] Testing Dispute Reporting & Admin Portal...", flush=True)
        issue = issues.report_issue(IssueCreate(
            order_id=created_order.id, category=IssueCategory.QUALITY_MISMATCH,
            title="Slight moisture in Batch C", description="Farmer C moisture was 14% instead of 11%."
        ), db, buyer)
        assert issue.status == IssueStatus.OPEN

        resolved = issues.resolve_issue(issue.id, IssueResolve(
            status=IssueStatus.RESOLVED, resolution_notes="Farmer C accepted Rs.100/tonne moisture discount."
        ), db, admin_user)
        assert resolved.status == IssueStatus.RESOLVED
        print(" Issue successfully resolved by Admin with notes.", flush=True)

        # Step 9: Admin Platform Statistics
        print("\n[Step 9] Fetching Admin Platform Overview Metrics...", flush=True)
        stats = admin.get_platform_statistics(db, admin_user)
        assert stats["users"]["total"] == 6
        assert stats["marketplace"]["orders"] >= 1
        print(" Admin stats:", stats, flush=True)

        print("\n==================================================================", flush=True)
        print(" ALL MODULES WEEKS 1 TO 8 VERIFIED 100% SUCCESSFULLY!             ", flush=True)
        print("==================================================================", flush=True)

    finally:
        db.close()
        if TEST_DB.exists():
            try:
                TEST_DB.unlink()
            except Exception:
                pass


if __name__ == "__main__":
    run_full_platform_verification()
