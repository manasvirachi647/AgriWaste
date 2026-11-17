from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.database import Base, engine
import app.models  # Ensures all models are registered in SQLAlchemy metadata
from app.routers import auth, listings, requirements


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Automatically create tables in development if they don't exist
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Backend API for AgriWaste Exchange - Connecting farmers with industrial residue buyers.",
    lifespan=lifespan,
)

# Enable CORS for mobile development (allows Expo development servers on LAN)
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
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "database": "connected",
        "version": settings.VERSION,
    }


# Include Routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(listings.router, prefix=settings.API_V1_STR)
app.include_router(requirements.router, prefix=settings.API_V1_STR)
