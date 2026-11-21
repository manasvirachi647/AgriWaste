from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.database import Base, engine
import app.models  # Ensures all models are registered in SQLAlchemy metadata
from app.routers import (
    auth,
    listings,
    requirements,
    matches,
    orders,
    transport,
    issues,
    admin,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Automatically create tables in development if they don't exist
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AgriWaste Exchange API - Complete Biomass Monetization & Rural Aggregation Platform",
    lifespan=lifespan,
)

# Enable CORS for mobile & web apps
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {
        "project": "AgriWaste Exchange API",
        "status": "online",
        "documentation": "/docs",
        "version": settings.VERSION,
        "modules": [
            "auth", "farmer_listings", "buyer_requirements",
            "smart_matching", "multi_farmer_orders", "transporter_logistics",
            "dispute_management", "admin_portal"
        ]
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "database": "connected",
        "version": settings.VERSION,
    }


# Include All Routers for Weeks 1 to 8
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(listings.router, prefix=settings.API_V1_STR)
app.include_router(requirements.router, prefix=settings.API_V1_STR)
app.include_router(matches.router, prefix=settings.API_V1_STR)
app.include_router(orders.router, prefix=settings.API_V1_STR)
app.include_router(transport.router, prefix=settings.API_V1_STR)
app.include_router(issues.router, prefix=settings.API_V1_STR)
app.include_router(admin.router, prefix=settings.API_V1_STR)
