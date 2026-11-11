# AgriWaste Exchange

**Agricultural Residue Monetization & Aggregation Platform**  
*Phase 1 & 2 Implementation (Weeks 1 & 2)*

---

## 🌾 Project Overview

AgriWaste Exchange is an Android mobile application and FastAPI backend system that connects farmers possessing surplus agricultural residue (such as rice husk, wheat straw, cotton stalks, sugarcane bagasse) with industrial biomass buyers and logistics aggregators.

---

## 📁 Repository Architecture

```text
AgriWaste/
├── AgriWaste_Exchange_Master_Project_Documentation.md
├── README.md
├── backend/
│   ├── app/
│   │   ├── core/
│   │   │   ├── config.py         # Application settings & environment vars
│   │   │   └── security.py       # Bcrypt hashing & PyJWT token generator
│   │   ├── database.py           # SQLAlchemy database engine & SessionLocal
│   │   ├── main.py               # FastAPI entry point & CORS configuration
│   │   ├── models/               # Relational Database Models
│   │   │   ├── user.py           # User, FarmerProfile, BuyerProfile, AggregatorProfile
│   │   │   ├── listing.py        # WasteListing (Farmer crop residue)
│   │   │   ├── requirement.py    # BuyerRequirement (Industrial biomass demands)
│   │   │   ├── match.py          # Match (Matching score engine records)
│   │   │   ├── order.py          # Order & OrderItem (Multi-farmer allocation)
│   │   │   ├── transport.py      # TransportJob (Logistics & pickups)
│   │   │   └── issue.py          # IssueReport (Disputes & resolutions)
│   │   ├── schemas/              # Pydantic Schemas
│   │   │   ├── auth.py           # Register, Login, Token payloads
│   │   │   ├── user.py           # User & Profile responses
│   │   │   └── listing.py        # Residue listing inputs & outputs
│   │   └── routers/
│   │       ├── deps.py           # JWT Authentication & RBAC Dependencies
│   │       ├── auth.py           # POST /auth/register, POST /auth/login, GET /auth/me
│   │       └── listings.py       # POST /listings, GET /listings, GET /listings/my
│   ├── tests/
│   │   └── test_auth_and_db.py   # Automated 10-step verification test suite
│   ├── requirements.txt
│   ├── .env.example
│   └── .env
└── mobile/
    ├── app/
    │   ├── _layout.tsx           # Expo Router Root Navigation Stack
    │   ├── index.tsx             # Welcome / Onboarding Screen
    │   ├── (auth)/
    │   │   ├── select-role.tsx   # Role Picker (Farmer, Buyer, Aggregator, Admin)
    │   │   ├── register.tsx      # Registration screen with dynamic role fields
    │   │   └── login.tsx         # Sign In screen with fast-fill demo credentials
    │   ├── (farmer)/
    │   │   └── dashboard.tsx     # Farmer Dashboard & Residue Management
    │   ├── (buyer)/
    │   │   └── dashboard.tsx     # Buyer Marketplace Feed & Demands
    │   ├── (aggregator)/
    │   │   └── dashboard.tsx     # Transporter Logistics & Pickup routes
    │   └── (admin)/
    │       └── dashboard.tsx     # Platform Overview & Moderation Portal
    ├── components/
    │   ├── Button.tsx            # Styled touchable button with loading state
    │   ├── Card.tsx              # Elevated surface container
    │   ├── Header.tsx            # Navigation header with role badges
    │   └── Input.tsx             # Text inputs with label & error handling
    ├── constants/
    │   └── colors.ts             # Agri-tech theme color palette
    ├── services/
    │   ├── api.ts                # Axios client with automated Bearer auth
    │   └── auth.ts               # Token management & authentication service
    ├── package.json
    ├── app.json
    └── tsconfig.json
```

---

## 🚀 Running the Week 1 & 2 Application

### 1. Backend (FastAPI + SQLAlchemy)

1. Navigate to the backend directory:
   ```powershell
   cd backend
   ```
2. Run the automated test suite to verify all auth, database, and role permissions:
   ```powershell
   python -u tests/test_auth_and_db.py
   ```
3. Start the FastAPI development server:
   ```powershell
   python -m uvicorn app.main:app --reload
   ```
4. Open the interactive Swagger API documentation in your browser:
   - **Interactive API Docs:** `http://127.0.0.1:8000/docs`
   - **Health Check:** `http://127.0.0.1:8000/health`

### 2. Mobile App (React Native + Expo)

1. Navigate to the mobile directory:
   ```powershell
   cd mobile
   ```
2. Install packages (when Node.js is installed):
   ```powershell
   npm install
   ```
3. Start the Expo development server:
   ```powershell
   npx expo start
   ```
4. Scan the generated QR code using the **Expo Go** app on your Android phone.

---

## ✅ Milestones Delivered (Weeks 1 & 2)

| Feature | Description | Status |
|---|---|---|
| **Architecture & Database Design** | Relational schema with 10 tables covering users, role profiles, waste listings, buyer requirements, multi-farmer orders, transport jobs, and disputes. | Complete |
| **Bcrypt Password Security** | Secure password hashing on registration with bcrypt. | Complete |
| **JWT Authentication** | Signed JSON Web Tokens issued on login and registration with expiry and payload encryption. | Complete |
| **Role-Based Access Control** | Dedicated roles (`farmer`, `buyer`, `aggregator`, `admin`) with backend permission enforcement. | Complete |
| **Residue Listings API** | Farmer residue listing creation and filtered retrieval by crop material and location. | Complete |
| **Mobile App Navigation & Screens** | Welcome screen, Role Selection, Registration, Login with demo accounts, and 4 dedicated Role Dashboards. | Complete |
| **Verification Test Suite** | 10-step automated backend test confirming database creation, authentication, role isolation, and listing flows. | Passed (100%) |
