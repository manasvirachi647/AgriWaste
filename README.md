# AgriWaste Exchange

**Agricultural Residue Monetization & Industrial Aggregation Platform**  
*Implementation Status: Phases 1 to 4 Complete (Weeks 1, 2, 3 & 4)*

---

## 🌾 Project Overview

AgriWaste Exchange is an Android mobile application and FastAPI backend system that connects farmers who have surplus crop residue (such as rice husk, wheat straw, cotton stalks, sugarcane bagasse) with industrial biomass buyers and logistics aggregators.

---

## 📁 Repository Architecture

```text
AgriWaste/
├── AgriWaste_Exchange_Master_Project_Documentation.md
├── README.md
├── backend/
│   ├── app/
│   │   ├── core/
│   │   │   ├── config.py             # Application settings & environment vars
│   │   │   └── security.py           # Bcrypt hashing & PyJWT token generator
│   │   ├── database.py               # SQLAlchemy database engine & SessionLocal
│   │   ├── main.py                   # FastAPI entry point & CORS configuration
│   │   ├── models/                   # Relational Database Models
│   │   │   ├── user.py               # User, FarmerProfile, BuyerProfile, AggregatorProfile
│   │   │   ├── listing.py            # WasteListing (Farmer crop residue)
│   │   │   ├── requirement.py        # BuyerRequirement (Industrial biomass demands)
│   │   │   ├── match.py              # Match (Matching score engine records)
│   │   │   ├── order.py              # Order & OrderItem (Multi-farmer allocation)
│   │   │   ├── transport.py          # TransportJob (Logistics & pickups)
│   │   │   └── issue.py              # IssueReport (Disputes & resolutions)
│   │   ├── schemas/                  # Pydantic Schemas
│   │   │   ├── auth.py               # Register, Login, Token payloads
│   │   │   ├── user.py               # User & Profile responses
│   │   │   ├── listing.py            # Residue listing inputs & outputs
│   │   │   └── requirement.py        # Buyer requirement inputs & outputs
│   │   └── routers/
│   │       ├── deps.py               # JWT Authentication & RBAC Dependencies
│   │       ├── auth.py               # POST /auth/register, POST /auth/login, GET /auth/me
│   │       ├── listings.py           # Farmer listings & discovery endpoints
│   │       └── requirements.py       # Buyer requirements & supplier matching
│   ├── tests/
│   │   ├── test_auth_and_db.py       # Phase 1 & 2 verification suite
│   │   └── test_farmer_and_buyer.py  # Phase 3 & 4 verification suite
│   ├── requirements.txt
│   ├── .env.example
│   └── .env
└── mobile/
    ├── app/
    │   ├── _layout.tsx               # Expo Router Navigation Stack
    │   ├── index.tsx                 # Welcome / Onboarding Screen
    │   ├── (auth)/
    │   │   ├── select-role.tsx       # Role Picker (Farmer, Buyer, Aggregator, Admin)
    │   │   ├── register.tsx          # Dynamic registration screen
    │   │   └── login.tsx             # Sign In screen with fast-fill demo logins
    │   ├── (farmer)/
    │   │   ├── dashboard.tsx         # Farmer Dashboard
    │   │   └── listings/
    │   │       ├── index.tsx         # Browse & filter all my residue listings
    │   │       ├── add.tsx           # Add crop residue listing form
    │   │       └── [id].tsx          # Listing details & matching buyer demands
    │   ├── (buyer)/
    │   │   ├── dashboard.tsx         # Buyer Procurement Dashboard
    │   │   └── requirements/
    │   │       ├── index.tsx         # Browse & filter all published requirements
    │   │       ├── add.tsx           # Publish biomass requirement form
    │   │       └── [id].tsx          # Requirement details & matching suppliers
    │   ├── (aggregator)/
    │   │   └── dashboard.tsx         # Transporter Dashboard
    │   └── (admin)/
    │       └── dashboard.tsx         # Platform Overview & Moderation Portal
    ├── components/
    │   ├── Button.tsx                # Reusable action button
    │   ├── Card.tsx                  # Elevated card container
    │   ├── Header.tsx                # Screen navigation header with role badges
    │   └── Input.tsx                 # Form input field with validation hints
    ├── constants/
    │   └── colors.ts                 # Agriculture & green tech color palette
    ├── services/
    │   ├── api.ts                    # Axios client with automated Bearer auth
    │   └── auth.ts                   # Token storage & auth methods
    ├── package.json
    ├── app.json
    └── tsconfig.json
```

---

## 🚀 Running the Project

### 1. Backend Server (FastAPI)

1. Open your terminal in the backend directory:
   ```powershell
   cd backend
   ```
2. Run the Phase 3 & 4 test suite:
   ```powershell
   python -u tests/test_farmer_and_buyer.py
   ```
3. Start the server with live reload:
   ```powershell
   python -m uvicorn app.main:app --reload
   ```
4. Access interactive documentation:
   - **Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
   - **Health Check:** [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

## ✅ Milestones Delivered (Phases 1 - 4)

| Phase / Week | Core Focus | Deliverables | Status |
|---|---|---|---|
| **Week 1** | Setup & Database | Relational database schema across 10 tables, FastAPI project setup, SQLite/PostgreSQL engine, CORS configuration. | Complete |
| **Week 2** | Auth & Security | Bcrypt password hashing, signed JWT token generation, role verification (`farmer`, `buyer`, `aggregator`, `admin`), login/registration mobile screens. | Complete |
| **Week 3** | Farmer Module | Crop residue listing creation (`POST /listings`), stock management, storage & moisture inputs, soil health advisory, farmer listing details, and discovery of matching buyer demands. | Complete |
| **Week 4** | Buyer Module | Industrial requirement publishing (`POST /requirements`), procurement progress tracking, plant delivery specifications, target price ranges, and discovery of matching farmer suppliers. | Complete |
