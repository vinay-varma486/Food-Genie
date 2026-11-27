# Food-Genie (FoodGenie) — AI-Powered Diet Planning, Nutrition Analytics & Health Platform

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18+-61DAFB?logo=react&logoColor=black)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-5.2+-646CFF?logo=vite&logoColor=white)](https://vitejs.dev/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.4+-38B2AC?logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![OpenRouter](https://img.shields.io/badge/OpenRouter-AI_Integration-6D28D9)](https://openrouter.ai/)

> **FoodGenie** is a full-stack AI nutrition, budget meal planning, and personal food analytics platform featuring **Genie** — an evidence-based multilingual AI assistant powered by OpenRouter.

---

## Key Features

- **Genie AI Assistant & Floating Chatbot**: Conversational nutrition guidance integrated with OpenRouter's OpenAI-compatible API (`openrouter_service.py`, `genie_ai_service.py`), fallback AI provider support (`gemini_service.py`), and automatic multilingual detection across **English**, **Telugu**, **Hindi**, **Tamil**, and **Kannada**.
- **Nutrition & Budget Analytics Dashboard**: Interactive SaaS dashboard (`DashboardView.jsx`, `BudgetAnalyticsSection.jsx`, `NutritionAnalyticsSection.jsx`) tracking total food budget, expenses, remaining balance, daily/weekly/monthly calorie & macro trends via Recharts, meal logging (`LogMealModal.jsx`), and visual health reports (`ReportsView.jsx`).
- **My Food Cart & PDF Meal Plan Export**: Save recommended food items across **Breakfast**, **Lunch**, **Evening Snacks**, and **Dinner** with quantity updates, macro/micronutrient & INR cost totals, persistent account storage, and clean multi-table PDF export (`GET /api/v1/cart/pdf` via ReportLab).
- **Food Explorer & Medical Restrictions**: Browse food datasets (`FoodExplorer.jsx`, `nutrition_service.py`) with calories, macros, key vitamins/minerals, health benefits, allergen checks, medical condition filtering, and drug-food interaction safeguards (`restriction_service.py`).
- **AI Budget Diet Planner & Smart Shopping List**: Generate 5-meal daily/weekly/monthly diet plans tailored to INR budgets (`BudgetPlannerView.jsx`, `ai_budget_planner.py`), save/update plans (`SavedPlansView.jsx`), and view categorized grocery lists with affordable swaps (`ShoppingListView.jsx`).
- **Location-Based Doctor & Clinic Finder**: Locate nearby physicians, dermatologists, dietitians, gastroenterologists, and endocrinologists using GPS or city coordinates with Haversine distance sorting and OpenStreetMap routing links (`DoctorFinderView.jsx`, `doctor_service.py`).
- **Authentication & Email OTP Verification**: Registration and login (`AuthModal.jsx`, `auth_service.py`) with Bcrypt password hashing, JWT authentication, and 6-digit email OTP verification (`email_service.py`).

---

## Technologies Used

| Layer | Stack & Libraries |
|---|---|
| **Backend API** | Python 3.11+, FastAPI, Uvicorn, Pydantic v2, Pydantic Settings |
| **AI & Messaging** | OpenRouter API (`nvidia/nemotron-3.5-super-vl:free` / OpenAI-compatible), HTTPX, Requests, SMTP / Resend email service |
| **Database & Migrations** | SQLAlchemy, Alembic, SQLite (local default via `init_db.py`), PostgreSQL (`psycopg2-binary`, `asyncpg`) |
| **Security & PDF** | Python-JOSE (JWT), Passlib & Bcrypt, ReportLab (PDF export) |
| **Frontend UI** | React 18, Vite 5, Tailwind CSS, Recharts, Lucide React, Framer Motion, Three.js / React Three Fiber |
| **Testing** | Pytest (`test_*.py` suites) and FastAPI `TestClient` E2E verification (`verify_all_endpoints.py`) |

---

## Project Folder Structure

All backend modules, frontend React components, configuration files, documentation, and test suites reside cleanly in the project root directory:

```text
FOODGENIE/
├── README.md                              # Project documentation and setup guide
├── DATABASE_SETUP.md                      # Database configuration & Alembic reference
├── DEPLOYMENT.md                          # Production deployment reference
├── .env.example                           # Safe environment variable template
├── .gitignore                             # Excludes .env, *.db, caches, node_modules & dist
├── requirements.txt                       # Python backend dependencies
├── package.json                           # Node.js frontend dependencies & Vite scripts
├── package-lock.json                      # Locked npm dependency tree
├── vite.config.js                         # Vite dev server & /api proxy configuration
├── tailwind.config.js                     # Tailwind CSS theme configuration
├── postcss.config.js                      # PostCSS plugin configuration
├── alembic.ini                            # Alembic migration configuration
├── alembic_env.py                         # Alembic migration environment script
├── alembic_migration_initial.py           # Initial Alembic schema revision
├── alembic_script.py.mako                 # Alembic migration template
│
├── index.html                             # SPA HTML entry point
├── index.css                              # Global Tailwind & custom styles
├── main.jsx                               # React root mount
├── App.jsx                                # Main application shell & view routing
├── api.js                                 # Frontend API client & auth headers
├── AuthContext.jsx                        # Authentication & session state provider
├── LanguageContext.jsx                    # Multilingual UI context provider
├── translations.js                        # Localized UI copy (en, te, hi, ta, kn)
├── ErrorBoundary.jsx                      # React error boundary fallback
├── Sidebar.jsx                            # Dashboard sidebar navigation
├── TopHeader.jsx                          # Header bar, date range & profile menu
├── Navbar.jsx                             # Navigation bar component
├── Home.jsx                               # Home Genie chat landing view
├── MainChatArea.jsx                       # Genie chat messages & structured responses
├── BottomChatInput.jsx                    # Chat prompt input & voice controls
├── FloatingGenieChat.jsx                  # Floating bottom-right Genie AI assistant
├── DashboardView.jsx                      # Nutrition & budget overview dashboard
├── BudgetAnalyticsSection.jsx             # Budget metrics & spending visualizations
├── NutritionAnalyticsSection.jsx          # Nutrient breakdown & daily progress charts
├── MyFoodCartView.jsx                     # Meal cart management & PDF export view
├── FoodExplorer.jsx                       # Searchable food & nutrient explorer
├── FoodCardDetailed.jsx                   # Detailed nutrition card with Add to Cart
├── FoodRestrictionCard.jsx                # Allergen & clinical warning card
├── GoalPlannerView.jsx                    # Health goal & diet restriction planner
├── BudgetPlannerView.jsx                  # INR budget diet plan generator
├── SavedPlansView.jsx                     # Saved diet plans manager
├── ShoppingListView.jsx                   # Categorized grocery checklist & swaps
├── DoctorFinderView.jsx                   # Nearby doctor & clinic search view
├── ReportsView.jsx                        # Analytics & nutrition summary reports
├── ProfileSettingsView.jsx                # User profile & preferences editor
├── MoreView.jsx                           # Additional FoodGenie tools & planners hub
├── About.jsx                              # About FoodGenie view
├── AuthModal.jsx                          # Sign in, sign up & Email OTP verification
├── ChatHistoryModal.jsx                   # Chat session history manager
├── LogMealModal.jsx                       # Quick meal logging modal
│
├── main.py                                # FastAPI application entry point & static SPA mount
├── config.py                              # Environment settings loader (.env)
├── database.py                            # SQLAlchemy engine & session setup
├── db_base.py                             # SQLAlchemy declarative Base
├── init_db.py                             # Verified nutrition dataset & table initializer
├── security.py                            # JWT creation & Bcrypt helpers
├── deps.py                                # FastAPI auth & DB dependencies
├── api_routes.py                          # Central API v1 router registration
├── api_*.py                               # Modular FastAPI routers (auth, profile, language, nutrition, recommendations, chat, budget, grocery, doctors, dashboard, cart)
├── model_*.py                             # SQLAlchemy ORM models
├── schema_*.py                            # Pydantic v2 request/response schemas
├── crud_*.py                              # Database CRUD operations
├── *_service.py                           # Business logic services (openrouter, genie_ai, genie, gemini, cart, pdf, dashboard, budget, meal_planner, nutrition, restriction, grocery, doctor, auth, email)
├── ai_budget_planner.py                   # 5-meal INR budget diet engine
├── genie_agent_config.py                  # Genie system prompt & clinical guardrails
├── language_detector.py                   # Script & transliteration language detector
│
├── verify_all_endpoints.py                # FastAPI TestClient end-to-end verification script
└── test_*.py                              # Automated pytest test suites (10 test modules)
```

> **Note:** Local secrets (`.env`), local runtime SQLite database (`foodgenie.db`), `node_modules/`, Vite build output (`dist/`), and Python caches are intentionally excluded via `.gitignore`.

---

## Installation Instructions

### Prerequisites
- **Python 3.11+**
- **Node.js 18+** and **npm**
- An **OpenRouter API key** (or optional Gemini / OpenAI / SMTP / Resend credentials)

### 1. Clone the Repository
```bash
git clone https://github.com/vinay-varma486/Food-Genie.git
cd Food-Genie
```

### 2. Backend Setup (Python)
```bash
# Create and activate a virtual environment
python -m venv .venv

# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1

# Linux / macOS
source .venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### 3. Frontend Setup (Node.js)
```bash
npm install
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env` and fill in your credentials (never commit `.env`):

```bash
# Windows (PowerShell)
Copy-Item .env.example .env

# Linux / macOS
cp .env.example .env
```

Key settings in `.env`:
- `SECRET_KEY`: Random hex secret for JWT signing
- `DATABASE_URL`: Defaults to `sqlite:///./foodgenie.db` (or set a PostgreSQL connection string)
- `OPENROUTER_API_KEY`: Your OpenRouter API key
- `OPENROUTER_BASE_URL`: `https://openrouter.ai/api/v1`
- `OPENROUTER_MODEL`: `nvidia/nemotron-3.5-super-vl:free`

---

## How to Run the Project

### Option A: Development Mode (Recommended)
Run the FastAPI backend and Vite frontend dev server in two terminals:

1. **Start Backend API (`http://127.0.0.1:8000`)**:
   ```bash
   uvicorn main:app --reload --port 8000
   ```
   - Swagger API Docs: `http://127.0.0.1:8000/docs`
   - Health Check: `http://127.0.0.1:8000/health`

2. **Start Frontend Dev Server (`http://127.0.0.1:5173`)**:
   ```bash
   npm run dev
   ```
   *(Vite automatically proxies `/api` and `/health` requests to `http://127.0.0.1:8000`.)*

### Option B: Single-Server Production Preview
Build the frontend static bundle into `dist/` and serve both UI and API through Uvicorn:

```bash
npm run build
uvicorn main:app --host 127.0.0.1 --port 8000
```
Open `http://127.0.0.1:8000` in your browser.

---

## Running Tests & Verification

Run the full automated backend test suite and endpoint verification script:

```bash
pytest -v
python verify_all_endpoints.py
```

---

## Disclaimer

FoodGenie provides AI-assisted nutritional education and meal planning tools for informational purposes only and is not a substitute for professional medical advice, diagnosis, or treatment.

*(Origin repository description: "Food-Genie: An simple diet planning website which is used for planning the day to day Meal.")*
