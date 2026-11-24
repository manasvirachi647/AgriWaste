from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import get_db
from app.core.security import hash_password, verify_password, create_access_token
from app.models.user import User, UserRole, FarmerProfile, BuyerProfile, AggregatorProfile
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from app.schemas.user import UserResponse
from app.routers.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new user (Farmer, Buyer, or Aggregator) and return JWT."""
    # Prevent public self-registration as Admin
    if data.role == UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Public registration as Admin is not permitted. Admin accounts must be provisioned by the system.",
        )

    # Check if username or email already exists
    existing = db.query(User).filter(
        or_(User.username == data.username, User.email == data.email)
    ).first()
    if existing:
        if existing.username == data.username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this username already exists.",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this email address already exists.",
            )

    # Prevent duplicate mobile/phone numbers if provided
    if data.phone_number and data.phone_number.strip():
        clean_phone = data.phone_number.strip()
        existing_phone = db.query(User).filter(User.phone_number == clean_phone).first()
        if existing_phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this mobile phone number already exists.",
            )

    # Hash password securely
    hashed_pwd = hash_password(data.password)

    # Create user
    new_user = User(
        username=data.username.strip().lower(),
        email=data.email.strip().lower(),
        hashed_password=hashed_pwd,
        full_name=data.full_name.strip(),
        phone_number=data.phone_number.strip() if data.phone_number else None,
        role=data.role,
        is_active=True,
    )
    db.add(new_user)
    db.flush()  # assign new_user.id

    # Create corresponding profile based on role
    if data.role == UserRole.FARMER:
        farmer_prof = FarmerProfile(
            user_id=new_user.id,
            farm_village=data.farm_village.strip() if data.farm_village else "Sanand",
            district=data.district.strip() if data.district else "Ahmedabad",
        )
        db.add(farmer_prof)
    elif data.role == UserRole.BUYER:
        buyer_prof = BuyerProfile(
            user_id=new_user.id,
            company_name=data.company_name.strip() if data.company_name else f"{data.full_name} Industries",
            industry_type=data.industry_type.strip() if data.industry_type else "Biomass / Biofuel",
        )
        db.add(buyer_prof)
    elif data.role == UserRole.AGGREGATOR:
        agg_prof = AggregatorProfile(
            user_id=new_user.id,
            vehicle_type=data.vehicle_type.strip() if data.vehicle_type else "Medium Commercial Truck",
            operating_district=data.district.strip() if data.district else "Ahmedabad",
        )
        db.add(agg_prof)

    db.commit()
    db.refresh(new_user)

    # Create JWT
    token = create_access_token(subject=new_user.id, role=new_user.role.value)

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse.model_validate(new_user)
    )


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate with username, email, or mobile phone and password, returning a signed JWT."""
    search_term = data.username_or_email.strip()
    user = db.query(User).filter(
        or_(
            User.username == search_term.lower(),
            User.email == search_term.lower(),
            User.phone_number == search_term,
        )
    ).first()

    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive. Please contact support.",
        )

    token = create_access_token(subject=user.id, role=user.role.value)

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )


@router.get("/me", response_model=UserResponse)
def get_my_profile(current_user: User = Depends(get_current_user)):
    """Get the profile of the currently authenticated user."""
    return current_user
