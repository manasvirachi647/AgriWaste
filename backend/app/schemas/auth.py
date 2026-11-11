from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from app.models.user import UserRole
from app.schemas.user import UserResponse


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)
    full_name: str = Field(..., min_length=2, max_length=100)
    phone_number: Optional[str] = None
    role: UserRole = UserRole.FARMER

    # Optional role profile setup fields on registration
    farm_village: Optional[str] = None
    district: Optional[str] = None
    company_name: Optional[str] = None
    industry_type: Optional[str] = None
    vehicle_type: Optional[str] = None


class LoginRequest(BaseModel):
    username_or_email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
