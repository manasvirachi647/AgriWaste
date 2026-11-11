# AgriWaste Exchange
## Complete Project Documentation and Mobile App Development Blueprint

**Project type:** Individual internship project  
**Platform:** Android mobile application (not a website)  
**Development approach:** Build a working prototype first, then improve it  
**Planned duration:** Approximately 8 weeks / 2 months  
**Primary domain:** Agriculture and environment

---

## 1. Project Overview

AgriWaste Exchange is a mobile application that connects farmers who have useful agricultural residue with industries and other buyers that can use that residue as raw material.

After harvesting, farmers may have crop residue such as rice husk, wheat straw, cotton stalks, sugarcane bagasse, groundnut shells and other biomass. Some residue is burned, dumped, left unused or sold through informal channels because farmers may not know who needs it, what price they can receive, or how to arrange transportation.

At the same time, industries may need agricultural biomass for activities such as energy generation, biomass fuel, packaging, paper production, composting or other suitable manufacturing processes. Finding a dependable supply from multiple farmers can be difficult.

AgriWaste Exchange aims to create a structured connection between these groups. Farmers can list available residue, buyers can publish requirements, and the application can identify suitable suppliers. When one farmer cannot fulfil a large order, the system can combine quantities from multiple farmers. Aggregators or transporters can coordinate collection and delivery.

The project is intended to make agricultural residue more useful, improve access to potential buyers, support responsible residue management and reduce avoidable waste. The app should not promise that all residue can or should be sold: farmers must retain the amount needed for soil health, livestock, household use and other local agricultural needs.

## 2. Problem Statement

Agricultural residue is often treated as waste even though some of it can be a useful resource. Farmers and potential buyers are not always connected through a transparent, convenient system.

Key problems include:

1. **Limited buyer discovery:** Farmers may not know which nearby industries or buyers need their residue.
2. **Uncertain demand and prices:** Farmers may not know the quantity, quality or price buyers expect.
3. **Scattered supply:** A buyer may need a large quantity, while each individual farmer may have only a small quantity available.
4. **Transportation difficulty:** Residue can be bulky, and transport costs may make a transaction impractical.
5. **Seasonal availability:** Different materials become available at different times of the year.
6. **Quality variation:** Moisture, contamination, storage and material condition can differ between suppliers.
7. **Trust and coordination:** Buyers and farmers need clear records of agreed quantities, collection, delivery and disputes.
8. **Quantity uncertainty:** A listed quantity may be an estimate rather than a verified quantity.
9. **Digital literacy and connectivity:** Some users may find complicated applications difficult or may have unreliable internet access.
10. **Responsible residue use:** Removing all crop residue can harm soil health or interfere with other useful agricultural practices.

## 3. Proposed Solution

AgriWaste Exchange provides a mobile platform with separate experiences for farmers, industrial buyers, aggregators/transporters and administrators.

- Farmers create listings describing the residue they can responsibly sell.
- Buyers publish requirements describing the material and quantity they need.
- A matching engine identifies suitable listings using material, quantity, distance, price, availability and available quality information.
- If one farmer cannot meet the requirement, the system can combine contributions from multiple farmers.
- An order records each farmer's contribution separately.
- An aggregator or transporter can coordinate collection and delivery.
- The buyer can confirm delivery, while the system maintains transaction and issue records.
- Admin users can review users, listings, orders and reported issues.

The first prototype should use transparent, rule-based matching. Machine learning should not be added until enough reliable data exists.

## 4. Main Objectives

1. Connect farmers with potential buyers of agricultural residue.
2. Make residue availability and buyer demand easier to discover.
3. Support matching based on practical transaction conditions.
4. Allow a large requirement to be fulfilled through multiple farmers.
5. Make transportation and order progress easier to coordinate.
6. Maintain records that improve transparency and accountability.
7. Encourage responsible residue use and avoid promoting harmful removal practices.
8. Build an accessible Android application that can be tested with realistic sample data.

## 5. Target Users and Application Roles

### 5.1 Farmer

A farmer can:
- Register and create a farmer profile.
- Add and manage agricultural residue listings.
- Enter material type, quantity, unit, expected price, location and availability.
- Add storage and quality details and upload photographs.
- View suitable buyer requirements or matching opportunities.
- Accept or reject an order contribution.
- Track collection and delivery progress.
- View transaction records and report a problem.

### 5.2 Industrial Buyer

A buyer can:
- Register and create a buyer/industry profile.
- Publish a requirement for a particular residue material.
- Specify the required quantity, preferred price range, delivery location, deadline and quality expectations.
- View matching suppliers.
- Review a combined supply proposal from multiple farmers.
- Confirm an order and track its progress.
- Confirm delivery or report a discrepancy.

### 5.3 Aggregator / Transporter

An aggregator or transporter can:
- Create a transporter profile.
- View assigned collection and delivery jobs.
- See pickup locations, quantities and delivery destination.
- Accept or update a transport job.
- Update collection, transit and delivery statuses.
- Record collected and delivered quantities.
- Report delays or problems.

### 5.4 Administrator

An administrator can:
- Review and manage user accounts.
- Review listings and buyer requirements.
- Monitor orders and transport jobs.
- Review reported issues and disputes.
- Manage inappropriate or inaccurate listings.
- View basic platform activity and transaction summaries.

Role permissions must be enforced by the backend, not only hidden or shown in the mobile interface.

## 6. Core Features

### 6.1 Registration, Login and User Profiles

- Registration and login for the supported user roles.
- Basic profile details and contact information.
- Role-based navigation after login.
- Secure password hashing on the backend.
- Token-based authentication.
- Users should only access records they are authorized to access.

### 6.2 Farmer Residue Listings

A listing should include:
- Residue/material name.
- Quantity and unit (for example, kg or tonnes).
- Expected price and pricing unit.
- Village/city or pickup location.
- Availability date or date range.
- Storage information.
- Quality details entered by the farmer.
- Optional photographs.
- Listing status: draft, available, partially reserved, reserved, completed or cancelled.

The application should distinguish between **estimated quantity** and **verified quantity**. The farmer's initial entry is not automatically a verified measurement.

### 6.3 Buyer Requirements

A buyer requirement should include:
- Required residue/material.
- Required quantity and unit.
- Target price or price range.
- Delivery location.
- Required-by date or delivery window.
- Quality expectations.
- Additional notes.

Buyers should be able to view, edit, close or cancel their requirements.

### 6.4 Matching Engine

The first version should use a transparent rule-based score. It should:
1. Filter out incompatible material types.
2. Check whether the listing is available.
3. Check whether the quantity and delivery timing are practical.
4. Score suitable listings using relevant factors.
5. Show why a listing is considered a good match.

Initial prototype weights (these are starting values for testing, not scientifically validated weights):

| Matching factor | Initial weight |
|---|---:|
| Material type compatibility | 30% |
| Quantity suitability | 20% |
| Distance | 20% |
| Price | 15% |
| Availability | 10% |
| Quality information | 5% |
| **Total** | **100%** |

The exact scoring formula and thresholds should be tested with sample cases and adjusted based on feedback. Material incompatibility should be treated as a hard filter rather than allowing a high score to compensate for the wrong material.

The interface should explain the score in simple terms, such as “same material”, “nearby pickup”, “quantity available” and “available within the requested period”.

### 6.5 Multiple-Farmer Order Allocation

A key feature is the ability to fulfil a large buyer requirement using contributions from multiple farmers.

**Example:**
- Buyer requests 10 tonnes of rice husk.
- Farmer A can supply 2 tonnes.
- Farmer B can supply 3 tonnes.
- Farmer C can supply 5 tonnes.
- The application combines these contributions into one buyer order.

The order has separate order-item records for each farmer. This preserves the source and quantity of every contribution.

The system should track:
- Requested quantity.
- Quantity offered by each farmer.
- Quantity accepted/committed.
- Quantity collected.
- Quantity delivered.
- Remaining quantity, if any.

**Important backend rule:** A listing must not be reserved or sold beyond its available quantity. Quantity reservation and order creation should be handled safely using a database transaction and appropriate locking/validation so that two buyers cannot reserve the same stock at the same time.

If the combined quantity is insufficient, the app should clearly show the remaining quantity instead of pretending that the order is fully fulfilled.

### 6.6 Transportation and Delivery

- Record pickup locations and buyer delivery location.
- Assign a transporter/aggregator where available.
- Show basic distance information.
- Provide an estimated transport cost using a configurable formula such as:

  `Estimated transport cost = Estimated distance × Rate per kilometre`

This is only a prototype estimate; real costs may also depend on vehicle type, load, road conditions, loading/unloading and local rates.

Suggested order statuses:

1. Requested
2. Accepted
3. Collection Scheduled
4. Collected
5. In Transit
6. Delivered
7. Completed

Also support cancellation and issue reporting. Keep each status update with its time and responsible user.

### 6.7 Quality and Verification

- Farmers provide declared quality and storage information.
- Photographs may help users inspect visible condition.
- A collection-stage verification can record actual collected quantity and visible condition.
- Store estimated and verified values separately.
- Do not claim that a photograph alone can accurately measure moisture content, calorific value or other laboratory properties.
- More advanced quality testing can be considered in future versions.

### 6.8 Trust, Reviews and Issue Reporting

- Maintain user profiles and order history.
- Allow a buyer or farmer to report an issue.
- Record issue category, description, related order and resolution status.
- Optional ratings/reviews can be added after a completed transaction.
- Admin users can review and resolve reported issues.

### 6.9 Notifications

Potential notifications:
- New matching opportunity.
- Buyer interest or order request.
- Order accepted or rejected.
- Collection scheduled.
- Material collected or delivered.
- Buyer confirmation.
- Issue update.

For the first prototype, in-app status updates are sufficient. Push notifications can be added after the core workflow works.

### 6.10 Language, Accessibility and Low Connectivity

- Keep screens simple and avoid unnecessary technical language.
- Use clear labels, large touch targets and straightforward forms.
- Plan for regional-language support; begin with a manageable set of languages and expand later.
- Save unfinished forms locally as drafts where practical.
- Handle failed requests with clear retry messages.
- Do not show a successful submission until the backend confirms it.
- Full offline synchronization is an advanced feature and should not delay the core prototype.

### 6.11 Responsible Residue Management

The app should remind farmers to list only the quantity they can responsibly sell. It should not encourage removal of all residue from fields. Farmers may need residue for soil cover, organic matter, livestock feed, household uses or other local purposes. Any future recommendation about a safe quantity should be based on credible agricultural guidance and local conditions, not an invented universal percentage.

## 7. Problems and Planned Solutions

| Challenge | Planned solution |
|---|---|
| Farmers may not know potential buyers | Show nearby and relevant buyer requirements |
| Farmers may find complex apps difficult | Simple screens, guided forms and regional-language support |
| Listed quantity may be inaccurate | Label quantities as estimated and record verified quantities separately |
| Buyers may struggle to find dependable supply | Rule-based matching with clear match reasons |
| Quality varies between suppliers | Capture declared details, photos and collection-stage verification |
| Transport can be expensive | Show distance and a configurable estimated transport cost |
| Supply is seasonal | Record availability dates and delivery windows |
| One farmer may not have enough quantity | Combine multiple farmers into one order using separate order items |
| Trust and disputes may be difficult | Profiles, transaction history, status records and issue reporting |
| Removing residue may affect soil health | Encourage responsible sale quantities and explain other uses |
| Not enough data for machine learning | Start with explainable rule-based matching |
| Internet may be unreliable | Local drafts, retry handling and clear network status |
| Limited internship time | Complete the core transaction flow before advanced features |

## 8. Technology Stack

The project must be developed as an **Android mobile application**, not as a website.

### 8.1 Mobile Application

- **React Native:** Build the Android app using JavaScript/TypeScript and native mobile components.
- **Expo:** Simplify development, testing and Android builds.
- **TypeScript:** Add type checking and improve code maintainability.
- **Expo Router:** Manage screen navigation.
- **Axios:** Send HTTP requests to the backend.
- **Expo SecureStore:** Store authentication tokens securely on the device.
- **Expo Image Picker:** Select listing photographs.
- **Expo Location:** Obtain location with user permission.
- **react-native-maps:** Display map locations if needed.

### 8.2 Backend

- **Python**
- **FastAPI:** Build REST APIs.
- **SQLAlchemy:** Interact with the database.
- **Alembic:** Manage database schema migrations.
- **JWT:** Token-based authentication.
- **Password hashing library:** Store password hashes rather than plain-text passwords.
- **Pydantic:** Validate incoming and outgoing API data.

### 8.3 Database

- **PostgreSQL:** Store users, profiles, listings, requirements, matches, orders and other structured records.
- PostGIS can be considered later if advanced geographic queries are needed. It is not essential for the first working prototype.

### 8.4 Development and Testing Tools

- Visual Studio Code.
- Node.js LTS and npm.
- Python.
- PostgreSQL and pgAdmin.
- Expo Go for early testing on an Android phone.
- Git and GitHub.
- Postman or FastAPI Swagger documentation (`/docs`) for API testing.
- Google Colab for optional data experiments if the local laptop is constrained.

### 8.5 Deployment

- EAS Build for Android builds.
- A hosted backend service for FastAPI.
- A managed PostgreSQL database.
- HTTPS for the deployed API.
- Keep credentials and secrets in environment variables, not in GitHub.

## 9. High-Level Architecture

```text
Android Mobile App
(React Native + Expo + TypeScript)
             |
             | HTTPS / REST API
             v
Python Backend (FastAPI)
             |
     ---------------------
     |         |         |
   Auth     Matching   Orders
     |         |         |
     ---------------------
             |
             v
       PostgreSQL
             |
     ---------------------
     |         |         |
   Users    Listings   Orders
             |
       Requirements
             |
      Order Items /
      Transport Jobs
```

The mobile application is the user interface. Business rules, authentication, authorization, matching, quantity validation and order creation should be handled by the backend. PostgreSQL stores the application records.

## 10. Suggested Mobile App Screen Structure

A possible Expo Router structure:

```text
mobile/
  app/
    _layout.tsx
    index.tsx
    (auth)/
      login.tsx
      register.tsx
      select-role.tsx
    (farmer)/
      dashboard.tsx
      listings/
        index.tsx
        add.tsx
        [id].tsx
      matches.tsx
      orders.tsx
      profile.tsx
    (buyer)/
      dashboard.tsx
      requirements/
        index.tsx
        add.tsx
        [id].tsx
      matches.tsx
      orders.tsx
      profile.tsx
    (aggregator)/
      dashboard.tsx
      jobs.tsx
      job-details.tsx
    (admin)/
      dashboard.tsx
      users.tsx
      listings.tsx
      orders.tsx
      issues.tsx
  components/
  services/
    api.ts
  constants/
  assets/
```

This is a suggested organization. The exact route structure can be adjusted as the app is implemented.

## 11. Backend Project Structure

```text
backend/
  app/
    main.py
    database.py
    models/
    schemas/
    routers/
      auth.py
      listings.py
      requirements.py
      matches.py
      orders.py
      transport.py
      issues.py
      admin.py
    services/
      matching.py
      allocation.py
      transport.py
    core/
      security.py
      config.py
  .env
  requirements.txt
```

Start with a small backend and add folders as the project grows. Do not create every module before the first endpoint works.

## 12. Database Design

Suggested tables:

| Table | Purpose |
|---|---|
| `users` | Login identity, password hash, role and basic account data |
| `farmer_profiles` | Farmer-specific profile information |
| `buyer_profiles` | Industry/buyer profile information |
| `aggregator_profiles` | Transporter/aggregator details |
| `waste_listings` | Residue listed by farmers |
| `buyer_requirements` | Materials and quantities requested by buyers |
| `matches` | Matching results and score explanations |
| `orders` | Main buyer order and overall status |
| `order_items` | Individual farmer contributions to an order |
| `transport_jobs` | Collection and delivery assignments |
| `payments` | Payment records/status; no payment gateway required initially |
| `reviews` | Optional reviews after completed transactions |
| `issue_reports` | Disputes, complaints and resolution records |

### Important relationships

- One user has one role and may have a role-specific profile.
- One farmer can create many waste listings.
- One buyer can create many requirements.
- One buyer requirement can have many matches.
- One order belongs to a buyer.
- One order can contain many order items.
- Each order item refers to the relevant farmer listing and records the contribution quantity and price.
- An order can have one or more transport jobs depending on the implementation.
- Issue reports can refer to the relevant user and/or order.

Use proper foreign keys, constraints and indexes. Store timestamps for important events. Store image URLs or storage references in the database rather than putting large image files directly into database rows.

## 13. Suggested API Endpoints

### Authentication

- `POST /auth/register`
- `POST /auth/login`
- `GET /auth/me`

### Farmer Listings

- `POST /listings`
- `GET /listings`
- `GET /listings/{listing_id}`
- `PATCH /listings/{listing_id}`
- `DELETE /listings/{listing_id}`

### Buyer Requirements

- `POST /requirements`
- `GET /requirements`
- `GET /requirements/{requirement_id}`
- `PATCH /requirements/{requirement_id}`
- `DELETE /requirements/{requirement_id}`

### Matching

- `GET /requirements/{requirement_id}/matches`

### Orders

- `POST /orders`
- `GET /orders`
- `GET /orders/{order_id}`
- `PATCH /orders/{order_id}/status`

### Transport

- `POST /transport/jobs`
- `GET /transport/jobs`
- `GET /transport/jobs/{job_id}`
- `PATCH /transport/jobs/{job_id}/status`

### Issues and Administration

- `POST /issues`
- `GET /issues`
- Admin-only endpoints to review users, listings, orders and issue reports.

These are initial endpoint names. Request/response schemas and permissions should be defined while implementing each feature.

## 14. Step-by-Step Development Procedure

Build the project in small working stages. Do not try to implement every feature at once.

### Phase 1 — Prepare the project

1. Create a project folder named `AgriWasteExchange`.
2. Create a Git repository and make an initial commit.
3. Create a short requirements document and list the core screens.
4. Install or verify Node.js LTS, npm, Python, Git and PostgreSQL.
5. Install Expo Go on the Android phone.
6. Use VS Code as the development editor.

Check installed tools in Windows PowerShell:

```powershell
node -v
npm -v
python --version
git --version
```

### Phase 2 — Create and run the Android app

From the project folder:

```powershell
npx create-expo-app@latest mobile
cd mobile
npx expo start
```

- Scan the QR code using Expo Go.
- Keep the computer and phone on the same Wi-Fi network.
- Confirm that the starter application opens on the phone.
- Keep the default TypeScript/Expo Router setup unless there is a specific reason to change it.

Build the initial screens in this order:
1. Welcome screen.
2. Role selection.
3. Login and registration screens.
4. Farmer dashboard.
5. Add listing screen.
6. Buyer dashboard.
7. Create requirement screen.

At first, use sample data to develop the screens and navigation. Connect the backend after the basic interface is understandable.

### Phase 3 — Create the FastAPI backend

From the main project folder:

```powershell
mkdir backend
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell prevents activation, use the environment's Python executable directly:

```powershell
.\.venv\Scripts\python.exe -m pip install "fastapi[standard]" sqlalchemy "psycopg[binary]" python-dotenv
```

If activation works, install the packages with:

```powershell
python -m pip install "fastapi[standard]" sqlalchemy "psycopg[binary]" python-dotenv
```

Create `main.py`:

```python
from fastapi import FastAPI

app = FastAPI(title="AgriWaste Exchange API")

@app.get("/")
def home():
    return {"message": "AgriWaste Exchange API is running"}

@app.get("/health")
def health():
    return {"status": "healthy"}
```

Run the server:

```powershell
python -m uvicorn main:app --reload
```

Open:
- `http://127.0.0.1:8000`
- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/docs`

The `/docs` page provides an interactive way to test API endpoints.

### Phase 4 — Set up PostgreSQL

1. Install PostgreSQL and pgAdmin if not already installed.
2. Create a database named `agriwaste_db`.
3. Create a `.env` file in the backend folder.
4. Add the database connection string, replacing the example password with the local PostgreSQL password:

```env
DATABASE_URL=postgresql+psycopg://postgres:YOUR_PASSWORD@localhost:5432/agriwaste_db
```

5. Add `.env` to `.gitignore`.
6. Never commit passwords, JWT secrets or other credentials to GitHub.
7. Create the SQLAlchemy engine, session and base model.
8. Add models gradually, beginning with users and waste listings.
9. Use Alembic migrations once the schema begins changing regularly.

A simplified SQLAlchemy database setup can be organized in `database.py`:

```python
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

In production, validate configuration and handle database connection errors safely. Do not expose credentials in logs.

### Phase 5 — Build the first complete feature: farmer listing

1. Create the `waste_listings` model.
2. Create a Pydantic schema for listing input and output.
3. Implement `POST /listings`.
4. Implement `GET /listings`.
5. Test both endpoints in `/docs`.
6. Connect the Add Listing screen to the API.
7. Fetch and display saved listings in the mobile app.

Example sample listing data:

```json
{
  "material": "Rice Husk",
  "quantity": 2,
  "unit": "tonnes",
  "price": 2500,
  "location": "Ahmedabad",
  "availability": "2026-11-20",
  "quality": "Stored in a dry covered area"
}
```

This is illustrative test data only; the application should not present it as a real market price.

Once authentication is implemented, the backend must obtain the farmer identity from the authenticated user token. Do not trust a farmer ID supplied by the mobile app as proof of ownership.

### Phase 6 — Connect the mobile app to the backend

Install Axios:

```powershell
cd mobile
npm install axios
```

Find the computer's local IPv4 address using:

```powershell
ipconfig
```

Create a mobile `.env` file:

```env
EXPO_PUBLIC_API_URL=http://YOUR_COMPUTER_IPV4:8000
```

For example, replace the placeholder with the computer's actual LAN address. On a physical phone, do not use `localhost` or `127.0.0.1` to reach the computer. The phone and computer generally need to be on the same Wi-Fi network, and the firewall must allow the connection.

Create `services/api.ts`:

```typescript
import axios from "axios";

export const api = axios.create({
  baseURL: process.env.EXPO_PUBLIC_API_URL,
  timeout: 10000,
});
```

Use the API client from screens/services to fetch and submit data. Restart Expo after changing environment variables.

**First end-to-end milestone:**

Farmer opens the app → enters a residue listing → taps Submit → mobile app calls FastAPI → FastAPI validates and saves the listing in PostgreSQL → app fetches and displays the saved listing.

Do not move to advanced features until this complete flow works.

### Phase 7 — Implement authentication and roles

1. Build registration and login API routes.
2. Hash passwords before saving them.
3. Issue a signed JWT after successful login.
4. Implement `GET /auth/me`.
5. Store the token securely using Expo SecureStore.
6. Add an Axios request interceptor to attach the token.
7. Show the correct dashboard for the user's role.
8. Enforce role and ownership permissions on every protected backend route.

### Phase 8 — Complete the farmer module

- Add listing form validation.
- List the farmer's own listings.
- Edit and cancel listings.
- Show listing status.
- Add image selection using Expo Image Picker.
- Store uploaded images in suitable file/object storage and keep their references in PostgreSQL.
- Track estimated, committed, collected and delivered quantities separately.

### Phase 9 — Complete the buyer module

- Create and manage buyer requirements.
- Add material, quantity, price range, delivery location, deadline and quality expectations.
- Display suitable listings and matching explanations.
- Allow the buyer to review a proposed multi-farmer supply.
- Let the buyer proceed to an order when the proposed supply is acceptable.

### Phase 10 — Implement rule-based matching

1. Retrieve open requirements and available listings.
2. Filter incompatible materials.
3. Check availability and basic quantity conditions.
4. Calculate a score using the initial weights.
5. Return ranked results with explanations.
6. Test cases where distance, price or quantity make a listing unsuitable.
7. Tune weights using sample scenarios and feedback.

Do not claim the matching is AI-powered or machine-learned if it is a rule-based scoring system.

### Phase 11 — Implement multi-farmer allocation

1. Let the buyer select or review suitable farmer contributions.
2. Calculate whether the total contribution meets the requirement.
3. Create one main order.
4. Create one `order_items` record for each farmer contribution.
5. Reserve the relevant listing quantities safely.
6. Use a database transaction so that either the complete allocation is saved or none of it is.
7. Prevent quantities from becoming negative or being reserved twice.
8. Support partial fulfilment and clearly show any remaining quantity.

### Phase 12 — Implement transport and order tracking

1. Create transport job records.
2. Assign an aggregator/transporter.
3. Record pickup and delivery locations.
4. Show basic distance and estimated transport cost.
5. Allow authorized users to update status.
6. Keep timestamps and the user responsible for each update.
7. Allow the buyer to confirm delivery.
8. Record any mismatch or issue.

Install location/map packages when the basic workflow is ready:

```powershell
npx expo install expo-location react-native-maps
```

Request location permission clearly and provide a manual location option where practical.

### Phase 13 — Add admin and trust features

- Admin dashboard.
- User and listing review.
- Order monitoring.
- Issue reporting and resolution.
- Basic transaction history.
- Optional reviews after successful orders.
- Basic in-app notifications or status indicators.

### Phase 14 — Test the complete app

Test each role separately and test the complete buyer-to-farmer workflow.

Important test cases:
- Invalid registration or login.
- A farmer submits missing or invalid listing data.
- A buyer requests a material that is unavailable.
- The available quantity is less than the buyer's requested quantity.
- Multiple farmers together can or cannot fulfil the requirement.
- Two buyers try to reserve the same listing quantity.
- A farmer edits or cancels a listing after it has been reserved.
- A transporter records partial collection or delivery.
- An order is cancelled.
- A user attempts to access another user's private records.
- The internet disconnects during submission.
- Location or photo permission is denied.
- An issue is reported and resolved.

Use Postman and FastAPI `/docs` to test backend behavior. Also test on a real Android device, not only an emulator or browser preview.

### Phase 15 — Prepare and deploy the Android prototype

1. Fix critical bugs.
2. Add app icon, name and basic visual consistency.
3. Prepare a demo account for each role using non-sensitive test data.
4. Deploy FastAPI to a hosting service.
5. Use a managed PostgreSQL database.
6. Configure environment variables and HTTPS.
7. Update the mobile API URL to the deployed HTTPS endpoint.
8. Configure EAS Build:

```powershell
npm install -g eas-cli
eas login
eas build:configure
eas build --platform android --profile preview
```

9. Install and test the resulting Android build.
10. Prepare a README, screenshots, architecture diagram, test cases and a short demonstration.

Build commands and deployment settings may change with the selected hosting provider and Expo configuration. Follow the current official documentation during deployment.

## 15. Suggested Eight-Week Work Plan

| Week | Main focus | Expected result |
|---|---|---|
| Week 1 | Requirements, app setup, backend setup and database design | Expo app runs on Android; FastAPI starts; database plan is ready |
| Week 2 | Database connection and authentication | Registration, login and role handling work |
| Week 3 | Farmer module | Farmer can create and view residue listings |
| Week 4 | Buyer module | Buyer can create and manage requirements |
| Week 5 | Matching and multi-farmer allocation | Suitable listings are ranked and combined into an order |
| Week 6 | Orders and logistics | Order and transport status can be tracked |
| Week 7 | Admin, quality, issue reporting and testing | Main roles and edge cases are tested |
| Week 8 | Bug fixing, Android build and documentation | Installable prototype and project documentation are ready |

The schedule is a guide. If time becomes limited, protect the core transaction flow before adding optional features.

## 16. Minimum Viable Product (MVP)

The first working prototype should prioritize:

1. Registration and login for farmer and buyer.
2. Farmer can create and manage a residue listing.
3. Buyer can create a residue requirement.
4. Matching can find suitable listings.
5. A buyer requirement can be fulfilled by multiple farmers.
6. An order can be created and tracked.
7. Basic collection/delivery status can be updated.
8. The application stores records in PostgreSQL.

Aggregator and admin screens can begin with simple functionality. More advanced capabilities should be added after the MVP works reliably.

## 17. Features for Later / Future Scope

These features are useful but should not block the first prototype:

- Machine-learning-based demand and price prediction.
- Advanced route optimization using tools such as OR-Tools.
- Automated vehicle/load planning.
- Image-based quality analysis.
- Laboratory or sensor-based quality integrations.
- Real payment gateway integration.
- Advanced analytics and environmental impact dashboards.
- Full offline synchronization.
- More regional languages and voice-assisted workflows.
- Integration with external agriculture, weather or market data sources.

A lack of reliable training data is a reason to start with rule-based matching rather than inventing an AI model.

## 18. Demonstration Scenario

Use one clear end-to-end demonstration:

1. Farmer A lists 2 tonnes of rice husk.
2. Farmer B lists 3 tonnes of rice husk.
3. Farmer C lists 5 tonnes of rice husk.
4. An industrial buyer requests 10 tonnes.
5. The matching system identifies the three listings.
6. The allocation module combines the contributions: 2 + 3 + 5 = 10 tonnes.
7. One order is created with three separate order items.
8. The aggregator receives a collection job.
9. Collection and delivery statuses are updated.
10. The buyer confirms delivery.
11. The order is marked completed and the transaction records remain available.

This demonstrates the project's central value: connecting scattered agricultural residue supply with a larger buyer requirement through one coordinated mobile workflow.

## 19. Development Priorities and Practical Rules

- Build one working feature at a time.
- Start with sample data, then connect real database records.
- Test every API before connecting its screen.
- Keep business rules in the backend.
- Never store plain-text passwords.
- Never commit `.env` files or secrets.
- Never trust user IDs or role values sent by the client without checking the authenticated account.
- Validate quantities and prevent overbooking.
- Preserve estimated and verified values separately.
- Use clear error messages and loading states.
- Do not claim that photos can verify technical quality measurements.
- Do not add machine learning just to label the project as AI.
- Do not let advanced features delay the core farmer-to-buyer order flow.
- Keep the app usable for people with limited digital experience.
- Treat environmental responsibility as a core product requirement.

## 20. First-Day Development Checklist

- [ ] Check Node.js and npm.
- [ ] Check Python.
- [ ] Check Git.
- [ ] Install or verify PostgreSQL.
- [ ] Install Expo Go on the Android phone.
- [ ] Create the `AgriWasteExchange` project folder.
- [ ] Create the Expo mobile app.
- [ ] Run the starter app on the phone.
- [ ] Create the backend folder and virtual environment.
- [ ] Install FastAPI and the initial backend dependencies.
- [ ] Run the FastAPI server.
- [ ] Open and test `/docs`.

**Immediate next development milestone:** Create the Expo project, run it successfully on the Android phone, and then create the basic FastAPI health-check endpoint. Once both run, connect the first farmer listing flow.

---

# 21. Daily Internship Tracker Entry

The following entry records the project planning and development-roadmap work completed in the latest discussion.

| Column | Content |
|---|---|
| **Title** | Project Development Planning |
| **Detail** | Studied the complete step-by-step process for developing the AgriWaste Exchange Android application. Finalized the development approach, selected the required technologies, and planned the development stages, including mobile app setup, backend development, database creation, user authentication, farmer and buyer modules, and the matching system. |
| **Remark** | Completed the initial development roadmap and understood the sequence of steps required to start building the application. |
| **Help** | Guidance was required for selecting the technology stack, setting up the development environment, understanding the app architecture, and planning the backend and database integration. |

---

## 22. Project Identity at a Glance

| Item | Current decision |
|---|---|
| Project name | AgriWaste Exchange |
| Project type | Individual internship project |
| Main domain | Agriculture and environment |
| Platform | Android mobile application |
| Mobile framework | React Native + Expo + TypeScript |
| Backend | Python + FastAPI |
| Database | PostgreSQL |
| Main users | Farmers, industrial buyers, aggregators/transporters and admin |
| Core mechanism | Residue listings, buyer requirements, rule-based matching, multi-farmer allocation and order tracking |
| First milestone | Run the Expo app on an Android phone and start the FastAPI backend |
| Development duration | Approximately 8 weeks |
| Main prototype objective | Demonstrate a buyer requirement being fulfilled through multiple farmers and tracked through delivery |

*This document consolidates the project concept, feature decisions, technical direction, development procedure, roadmap and latest tracker entry discussed so far. Implementation details may be refined as the prototype is tested with users and realistic data.*
