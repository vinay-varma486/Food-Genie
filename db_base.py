# Import all the models, so that Base has them before being
# imported by Alembic
from database import Base
from model_user import User, UserProfile, Allergy
from model_nutrition import FoodItem, Nutrient, FoodNutrient, SavedFood
from model_chat import ChatHistory
from model_recommendation import Recommendation, DietPlan
from model_grocery import GroceryItem

