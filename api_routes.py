from fastapi import APIRouter
import api_auth
import api_profile
import api_language
import api_nutrition
import api_recommendations
import api_chat
import api_budget
import api_grocery
import api_doctors
import api_dashboard
import api_cart

api_router = APIRouter()

api_router.include_router(api_auth.router)
api_router.include_router(api_profile.router)
api_router.include_router(api_language.router)
api_router.include_router(api_nutrition.router)
api_router.include_router(api_recommendations.router)
api_router.include_router(api_chat.router)
api_router.include_router(api_budget.router)
api_router.include_router(api_grocery.router)
api_router.include_router(api_doctors.router)
api_router.include_router(api_dashboard.router)
api_router.include_router(api_cart.router)
