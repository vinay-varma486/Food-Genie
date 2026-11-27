import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from api_routes import api_router
from database import SessionLocal
from init_db import init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("foodgenie")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize DB tables and seed verified nutrition dataset
    logger.info("Initializing FoodGenie database and verified nutrition datasets...")
    db = SessionLocal()
    try:
        init_db(db)
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
    finally:
        db.close()
    yield
    # Shutdown logic if any
    logger.info("FoodGenie backend shutting down.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="""
# FoodGenie — AI-Powered Food & Nutrition Recommendation Platform API

FoodGenie provides personalized, scientifically verified nutrition advice through an AI assistant named **GENIE**.

### Key Modules:
- **Authentication**: JWT token-based auth with secure bcrypt password hashing.
- **User Profiles & Language Preferences**: Stores user language (`en`, `te`, `hi`, `ta`, `kn`), dietary preferences, and allergy triggers.
- **Nutritional Information**: Verified USDA / ICMR nutrient database with regional names (Telugu, Hindi).
- **AI Recommendations**: Genie prompt orchestrator returning tailored food advice, benefits, and safety warnings.
- **Chat History**: Full conversation logging with language code and voice metadata.
- **AI Nutrition Intelligence**: Pure text AI diet and wholefood planner powered by Gemini.
- **Budget Planner**: Cost-optimized monthly and daily meal budget allocations in INR.
- **Grocery Planner**: Affordable local staples and smart high-cost swaps.
- **Doctor Finder**: Certified clinical dietitians and nutritionists with OpenStreetMap live geo-distance.
    """,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Modular API Router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Nutrition & AI Health Diagnostics Endpoints
from api_nutrition import calculate_water_intake
from gemini_service import GenieGeminiService
from openrouter_service import GenieOpenRouterService, openrouter_service

app.add_api_route(
    "/api/nutrition/water-intake",
    calculate_water_intake,
    methods=["POST"],
    tags=["Nutritional Information & Food Items"],
    summary="Smart Water Intake Calculator (/api/nutrition/water-intake)"
)

@app.get("/api/health/openrouter", tags=["Health & Status"], summary="Real-Time OpenRouter AI Health & Latency Check")
def openrouter_health_check():
    """Performs real-time generation test against OpenRouter OpenAI-compatible API with latency reporting."""
    service = GenieOpenRouterService()
    return service.test_health()

@app.get("/api/health/gemini", tags=["Health & Status"], summary="Real-Time Gemini API Health & Latency Check")
def gemini_health_check():
    """Performs real-time generation test against Google Gemini API with latency reporting."""
    service = GenieGeminiService()
    return service.test_health()



@app.get("/api/status", tags=["Health & Status"])
def api_status():
    active_provider = (
        "openrouter" if openrouter_service.is_configured()
        else ("gemini" if settings.GEMINI_API_KEY else "internal")
    )
    return {
        "app": "FoodGenie API",
        "assistant": "Genie",
        "status": "online",
        "ai_provider": active_provider,
        "ai_model": openrouter_service.model if active_provider == "openrouter" else settings.LLM_PROVIDER,
        "version": settings.VERSION,
        "docs": "/docs",
        "supported_languages": settings.SUPPORTED_LANGUAGES
    }

@app.get("/health", tags=["Health & Status"])
def health_check():
    return {"status": "healthy", "service": "foodgenie-fastapi"}

# Mount built 3D React Frontend if available
import os
from fastapi.staticfiles import StaticFiles

frontend_dist_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "dist"))
if os.path.isdir(frontend_dist_path):
    logger.info(f"Mounting compiled frontend from: {frontend_dist_path}")
    app.mount("/", StaticFiles(directory=frontend_dist_path, html=True), name="frontend")
else:
    @app.get("/", tags=["Health & Status"])
    def root():
        return {
            "app": "FoodGenie API",
            "assistant": "Genie",
            "status": "online",
            "version": settings.VERSION,
            "docs": "/docs",
            "supported_languages": settings.SUPPORTED_LANGUAGES
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

