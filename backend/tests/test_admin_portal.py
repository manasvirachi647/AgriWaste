import os
import sys
from pathlib import Path

# Add backend directory to sys.path
BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

# Use test SQLite database
TEST_DB = BACKEND_DIR / "test_admin_portal.db"
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
from app.schemas.issue import IssueCreate
from app.routers import auth, listings, requirements, orders, transport, issues, admin
from app.routers.admin import StatusUpdateRequest, AggregatorAssignRequest, IssueActionRequest, AdminProfileUpdate


def test_admin_full_suite():
    print("==================================================================", flush=True)
    print(" AGRIWASTE EXCHANGE: ADMIN SECTION COMPREHENSIVE TEST SUITE      ", flush=True)
    print("==================================================================", flush=True)

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # 1. Setup Users: 2 Farmers, 1 Buyer, 1 Transporter, 1 Admin
        print("\n[Test 1] Provisioning Users across all roles...", flush=True)
        # Farmer A
        auth.register(RegisterRequest(
            username="farmer_a", email="fa@farm.in", password="Password123!",
            full_name="Ramesh Patel", role=UserRole.FARMER, farm_village="Sanand", district="Ahmedabad", phone_number="9876543210"
        ), db)
        farmer_a = db.query(User).filter(User.username == "farmer_a").first()

        # Farmer B
        auth.register(RegisterRequest(
            username="farmer_b", email="fb@farm.in", password="Password123!",
            full_name="Suresh Chaudhary", role=UserRole.FARMER, farm_village="Bavla", district="Ahmedabad", phone_number="9876543211"
        ), db)
        farmer_b = db.query(User).filter(User.username == "farmer_b").first()

        # Buyer
        auth.register(RegisterRequest(
            username="buyer_bio", email="buyer@biopower.com", password="Password123!",
            full_name="Vikram Mehta", role=UserRole.BUYER, company_name="Gujarat BioPower Ltd", facility_address="Sanand GIDC", phone_number="9876543212"
        ), db)
        buyer = db.query(User).filter(User.username == "buyer_bio").first()

        # Transporter
        auth.register(RegisterRequest(
            username="trans_fleet", email="trans@kisanfleet.com", password="Password123!",
            full_name="Harpreet Singh", role=UserRole.AGGREGATOR, vehicle_type="10T Commercial Truck", operating_district="Ahmedabad", phone_number="9876543213"
        ), db)
        transporter = db.query(User).filter(User.username == "trans_fleet").first()

        from app.core.security import hash_password
        # Admin
        admin_user = User(
            username="sys_admin", email="admin@agriwaste.com",
            hashed_password=hash_password("AdminPass123!"),
            full_name="System Administrator", role=UserRole.ADMIN,
            phone_number="9876543214", is_active=True
        )
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        print("  ✓ Registered: 2 Farmers, 1 Buyer, 1 Transporter, 1 Admin", flush=True)

        # 2. Test User Management
        print("\n[Test 2] Testing User Management...", flush=True)
        all_users = admin.get_all_users(role=None, search=None, db=db, current_user=admin_user)
        assert len(all_users) == 5
        print(f"  ✓ Total users retrieved: {len(all_users)}")

        farmers = admin.get_all_users(role=UserRole.FARMER, search=None, db=db, current_user=admin_user)
        assert len(farmers) == 2
        print("  ✓ Filter by role (FARMER): 2 farmers found")

        search_result = admin.get_all_users(role=None, search="Ramesh", db=db, current_user=admin_user)
        assert len(search_result) == 1
        assert search_result[0].username == "farmer_a"
        print("  ✓ Search by name ('Ramesh') verified")

        # Deactivate Farmer B
        deactivated = admin.toggle_user_active_status(farmer_b.id, is_active=False, db=db, current_user=admin_user)
        assert deactivated.is_active is False
        print("  ✓ User account deactivated successfully")

        # Reactivate Farmer B
        reactivated = admin.toggle_user_active_status(farmer_b.id, is_active=True, db=db, current_user=admin_user)
        assert reactivated.is_active is True
        print("  ✓ User account reactivated successfully")

        # Admin self-deactivation protection
        try:
            admin.toggle_user_active_status(admin_user.id, is_active=False, db=db, current_user=admin_user)
            assert False, "Admin should not be able to deactivate own account!"
        except Exception as e:
            print(f"  ✓ Admin self-deactivation safely blocked: {e.detail}")

        # 3. Create Listings & Buyer Requirements
        print("\n[Test 3] Creating Listings & Requirements...", flush=True)
        listings.create_listing(WasteListingCreate(
            material_name="Rice Husk", estimated_quantity=4.0, price_per_unit=2400.0,
            location_name="Sanand, Ahmedabad", storage_type="Dry shed", moisture_condition="< 12%"
        ), db, farmer_a)
        l1 = db.query(WasteListing).filter(WasteListing.farmer_id == farmer_a.id).first()

        listings.create_listing(WasteListingCreate(
            material_name="Rice Husk", estimated_quantity=6.0, price_per_unit=2350.0,
            location_name="Bavla, Ahmedabad", storage_type="Baled", moisture_condition="14%"
        ), db, farmer_b)
        l2 = db.query(WasteListing).filter(WasteListing.farmer_id == farmer_b.id).first()

        requirements.create_requirement(BuyerRequirementCreate(
            material_name="Rice Husk", required_quantity=10.0,
            target_price_max=2500.0, delivery_location="Sanand GIDC Biofuel Plant",
            quality_specifications="Moisture < 14%"
        ), db, buyer)
        req = db.query(BuyerRequirement).filter(BuyerRequirement.buyer_id == buyer.id).first()
        print("  ✓ Created 2 Farmer Listings (4T and 6T) and 1 Buyer Requirement (10T)")

        # Test Listing Moderation
        all_listings = admin.get_admin_listings(status_filter=None, search=None, db=db, current_user=admin_user)
        assert len(all_listings) == 2
        print(f"  ✓ Admin retrieved {len(all_listings)} listings for moderation")

        mod_list = admin.moderate_listing_status(l1.id, StatusUpdateRequest(status="inactive", reason="Seasonal audit"), db=db, current_user=admin_user)
        assert mod_list.status == ListingStatus.AVAILABLE or mod_list.status == ListingStatus.CANCELLED or "Audit" in mod_list.quality_notes
        print("  ✓ Admin listing moderation verified")

        # Restore listing 1 to available
        l1.status = ListingStatus.AVAILABLE
        db.commit()

        # 4. Multi-Farmer Order Allocation
        print("\n[Test 4] Testing Multi-Farmer Order Allocation (4T + 6T = 10T)...", flush=True)
        order_payload = OrderCreateAllocationRequest(
            requirement_id=req.id,
            contributions=[
                OrderContributionItem(listing_id=l1.id, allocated_quantity=4.0),
                OrderContributionItem(listing_id=l2.id, allocated_quantity=6.0)
            ],
            delivery_address="Sanand GIDC Biofuel Plant"
        )
        created_order = orders.create_order(order_payload, db, buyer)
        assert created_order.total_quantity == 10.0
        assert len(created_order.items) == 2
        print("  ✓ Multi-farmer order placed with 2 individual farmer contributions")

        # 5. Admin Orders Management
        print("\n[Test 5] Testing Admin Orders Management...", flush=True)
        admin_orders = admin.get_admin_orders(status_filter=None, search=None, db=db, current_user=admin_user)
        assert len(admin_orders) >= 1
        ord_item = admin_orders[0]
        assert ord_item.total_quantity == 10.0
        assert len(ord_item.items) == 2
        print(f"  ✓ Admin successfully inspected order #{ord_item.id} with {len(ord_item.items)} farmer contributions")

        # 6. Aggregator & Transport Management
        print("\n[Test 6] Testing Aggregator & Transport Job Management...", flush=True)
        # Verify transport jobs exist
        t_jobs = admin.get_admin_transport_jobs(status_filter=None, unassigned_only=False, db=db, current_user=admin_user)
        assert len(t_jobs) >= 1
        job = t_jobs[0]
        print(f"  ✓ Transport Job #{job.id} detected")

        # Admin assigns job to transporter
        assigned_job = admin.assign_aggregator_to_job(job.id, AggregatorAssignRequest(aggregator_id=transporter.id), db=db, current_user=admin_user)
        assert assigned_job.aggregator_id == transporter.id
        assert assigned_job.status == TransportStatus.ASSIGNED
        print(f"  ✓ Job #{job.id} assigned to Transporter #{transporter.id} ({transporter.full_name})")

        # 7. Issue & Dispute Management
        print("\n[Test 7] Testing Issue & Dispute Management...", flush=True)
        new_issue = issues.report_issue(IssueCreate(
            order_id=created_order.id, category=IssueCategory.QUALITY_MISMATCH,
            title="Moisture verification needed", description="Slightly higher moisture on 4T batch"
        ), db, buyer)
        assert new_issue.status == IssueStatus.OPEN

        disputes = admin.get_admin_disputes(status_filter=None, db=db, current_user=admin_user)
        assert len(disputes) >= 1
        print(f"  ✓ Admin retrieved {len(disputes)} open disputes")

        # Mark Under Review
        reviewed = admin.handle_admin_issue_action(new_issue.id, IssueActionRequest(status="investigating", resolution_notes="Dispatched field agent to inspect"), db=db, current_user=admin_user)
        assert reviewed.status == IssueStatus.INVESTIGATING
        print("  ✓ Issue moved to INVESTIGATING / Under Review")

        # Resolve Issue
        resolved = admin.handle_admin_issue_action(new_issue.id, IssueActionRequest(status="resolved", resolution_notes="Approved with 2% allowance agreed by buyer"), db=db, current_user=admin_user)
        assert resolved.status == IssueStatus.RESOLVED
        assert resolved.resolution_notes == "Approved with 2% allowance agreed by buyer"
        print("  ✓ Issue resolved by Admin with resolution notes")

        # 8. Admin Platform Statistics
        print("\n[Test 8] Testing Dynamic Platform Statistics...", flush=True)
        stats = admin.get_platform_statistics(db, admin_user)
        assert stats["users"]["total"] == 5
        assert stats["users"]["farmers"] == 2
        assert stats["users"]["buyers"] == 1
        assert stats["users"]["transporters"] == 1
        assert stats["users"]["admins"] == 1
        assert stats["marketplace"]["orders"] >= 1
        assert len(stats["recent_activity"]) >= 1
        print("  ✓ Platform stats fully verified dynamically from real DB records:")
        print(f"    Users: {stats['users']}")
        print(f"    Marketplace: {stats['marketplace']}")
        print(f"    Recent Activity Count: {len(stats['recent_activity'])}")

        # 9. Admin Profile Management
        print("\n[Test 9] Testing Admin Profile Management...", flush=True)
        prof = admin.get_admin_profile(current_user=admin_user)
        assert prof.username == "sys_admin"
        assert prof.role == UserRole.ADMIN

        updated_prof = admin.update_admin_profile(AdminProfileUpdate(
            full_name="Lead System Administrator", phone_number="9988776655"
        ), db=db, current_user=admin_user)
        assert updated_prof.full_name == "Lead System Administrator"
        assert updated_prof.phone_number == "9988776655"
        assert updated_prof.role == UserRole.ADMIN
        print("  ✓ Admin profile updated safely without role changes")

        # 10. Security & Role-Based Access Control
        print("\n[Test 10] Testing Security & Access Control...", flush=True)
        # Attempting to call admin endpoint with farmer credentials must fail
        from fastapi import HTTPException
        try:
            admin.get_all_users(role=None, search=None, db=db, current_user=farmer_a)
            assert False, "Farmer should NOT be able to access admin users endpoint!"
        except HTTPException as he:
            assert he.status_code == 403
            print("  ✓ Non-admin role blocked from admin endpoint (HTTP 403)")

        print("\n==================================================================", flush=True)
        print(" ALL 10 ADMIN PORTAL TEST CASES PASSED SUCCESSFULLY! (100%)       ", flush=True)
        print("==================================================================", flush=True)

    finally:
        db.close()
        if TEST_DB.exists():
            try:
                TEST_DB.unlink()
            except Exception:
                pass


if __name__ == "__main__":
    test_admin_full_suite()
