# FoodGenie Database Setup & Migration Guide

This guide details the complete database configuration, migrations, and verified nutritional seed data setup for **FoodGenie**.

---

## 1. Supported Databases

- **PostgreSQL 14+** (Recommended for Production)
- **SQLite 3** (Default for Local Development & Testing)

The database dialect is governed by the `DATABASE_URL` environment variable in `backend/.env`.

---

## 2. PostgreSQL Setup (Production)

### A. Install PostgreSQL
- **Ubuntu/Debian**:
  ```bash
  sudo apt update
  sudo apt install postgresql postgresql-contrib
  sudo systemctl start postgresql
  ```
- **macOS (Homebrew)**:
  ```bash
  brew install postgresql@15
  brew services start postgresql@15
  ```
- **Windows**:
  Download and run the installer from [postgresql.org](https://www.postgresql.org/download/windows/).

### B. Create Database and User
Log in as the `postgres` superuser:
```bash
sudo -u postgres psql
```

Run the following SQL commands:
```sql
CREATE DATABASE foodgenie_db;
CREATE USER foodgenie_user WITH ENCRYPTED PASSWORD 'your_strong_password_here';
GRANT ALL PRIVILEGES ON DATABASE foodgenie_db TO foodgenie_user;
ALTER DATABASE foodgenie_db OWNER TO foodgenie_user;
\q
```

### C. Update `backend/.env`
Configure `DATABASE_URL` in `backend/.env`:
```env
DATABASE_URL="postgresql://foodgenie_user:your_strong_password_here@localhost:5432/foodgenie_db"
```

---

## 3. Database Migrations (Alembic)

FoodGenie uses Alembic for declarative schema versioning and schema migrations.

### Step 1: Initialize Database Tables
Navigate to the `backend/` directory:
```bash
cd backend
```

Ensure your Python virtual environment is activated and dependencies installed:
```bash
pip install -r requirements.txt
```

### Step 2: Apply Migrations
Apply all schema migrations to target head revision:
```bash
alembic upgrade head
```

### Step 3: Seed Verified Nutritional & Clinical Data
FoodGenie comes with a comprehensive seed dataset containing verified foods from **ICMR-NIN Indian Food Composition Tables (IFCT)** and **USDA FoodData Central**, RDA benchmarks, and grocery items.

Run the seeder:
```bash
python -c "from app.db.session import SessionLocal; from app.db.init_db import init_db; db = SessionLocal(); init_db(db); db.close(); print('Database initialized and seeded successfully!')"
```

---

## 4. SQLite Setup (Local Development)

SQLite works out-of-the-box without installing external services:
```env
DATABASE_URL="sqlite:///./foodgenie.db"
```

When you start the FastAPI backend or run the tests, tables and seed data are automatically initialized on first startup if not already present.

---

## 5. Schema Reference & Table Architecture

| Table Name | Entity Description | Key Columns |
|---|---|---|
| `users` | Core user credentials & authentication | `id`, `email`, `hashed_password`, `full_name`, `is_active` |
| `user_profiles` | Personalized health & nutrition settings | `id`, `user_id`, `preferred_language`, `dietary_preference`, `monthly_food_budget`, `daily_calorie_target`, `health_conditions`, `city` |
| `allergies` | Recorded allergens and sensitivities | `id`, `profile_id`, `allergen_name`, `severity`, `notes` |
| `food_items` | Verified whole foods & regional staples | `id`, `name`, `name_te`, `name_hi`, `category`, `calories_kcal`, `protein_g`, `carbs_g`, `fat_g`, `fiber_g`, `serving_size`, `preparation_methods` |
| `nutrients` | Essential vitamins, minerals & RDAs | `id`, `name`, `nutrient_code`, `category`, `daily_rda_adult`, `unit`, `physiological_role` |
| `food_nutrients` | Nutrient association per food (IFCT/USDA) | `id`, `food_item_id`, `nutrient_id`, `amount_per_100g`, `percent_daily_value` |
| `recommendations`| Recorded Genie AI nutritional outputs | `id`, `user_id`, `query`, `intent`, `language`, `summary`, `recommended_foods`, `foods_to_avoid` |
| `chat_history` | Multilingual conversation threads | `id`, `user_id`, `session_id`, `user_query`, `genie_response`, `language_code`, `is_voice_input` |
| `diet_plans` | Saved 5-meal daily and weekly schedules | `id`, `user_id`, `title`, `duration_type`, `estimated_cost_inr`, `meals_plan_data`, `grocery_checklist` |
| `grocery_items` | Regional grocery staples & price metrics | `id`, `name`, `category`, `standard_quantity`, `avg_price_inr`, `is_budget_hero`, `affordable_substitute_for` |
| `saved_foods` | User bookmarked food items | `id`, `user_id`, `food_id`, `notes`, `created_at` |

---

## 6. Verifying Database Setup

Execute the automated backend test suite to verify database connectivity and table relations:
```bash
cd backend
python -m pytest tests/test_full_app_integration.py -v
```
A passing output confirms that the database engine, sessions, schema relationships, and seed datasets are functional.

