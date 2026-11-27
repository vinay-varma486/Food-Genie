from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from deps import get_db, get_current_user, get_optional_user
from model_user import User
from schema_nutrition import (
    FoodItemResponse, FoodNutrientResponse, SavedFoodCreate, SavedFoodResponse, NutrientResponse,
    WaterIntakeRequest, WaterIntakeResponse, HourlyScheduleItem
)
from crud_nutrition import (
    get_food_items, get_food_item_by_id, get_food_nutrients, get_nutrients,
    save_food_for_user, get_saved_foods_by_user, remove_saved_food
)

router = APIRouter(prefix="/nutrition", tags=["Nutritional Information & Food Items"])

@router.get(
    "/foods",
    response_model=List[FoodItemResponse],
    summary="List verified foods catalog",
    description="Lists or searches verified whole foods with macronutrients and regional names."
)
@router.get(
    "/search",
    response_model=List[FoodItemResponse],
    summary="Search verified foods, vegetables, and regional staples",
    description="Searches verified foods with macronutrients and regional names (English, Telugu, Hindi)."
)
def search_foods(
    query: Optional[str] = None,
    category: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    # Ensure query and category are strings if FastAPI Query params are provided
    clean_query = str(query) if (query and not hasattr(query, 'default')) else None
    clean_category = str(category) if (category and not hasattr(category, 'default')) else None
    items = get_food_items(db, query=clean_query, category=clean_category, skip=skip, limit=limit)
    response = []
    for item in items:
        nutrients = get_food_nutrients(db, item.id)
        nutrient_list = [
            FoodNutrientResponse(
                id=fn.id,
                nutrient_name=fn.nutrient.name,
                nutrient_category=fn.nutrient.category,
                amount_per_100g=fn.amount_per_100g,
                unit=fn.unit,
                percent_daily_value=fn.percent_daily_value
            )
            for fn in nutrients if fn.nutrient
        ]
        res_item = FoodItemResponse(
            id=item.id,
            name=item.name,
            name_te=item.name_te,
            name_hi=item.name_hi,
            scientific_name=item.scientific_name,
            category=item.category,
            calories_kcal=item.calories_kcal,
            protein_g=item.protein_g,
            carbs_g=item.carbs_g,
            fat_g=item.fat_g,
            fiber_g=item.fiber_g,
            glycemic_index=item.glycemic_index,
            description=item.description,
            benefits_summary=item.benefits_summary,
            cautions=item.cautions,
            verified_source=item.verified_source,
            nutrients=nutrient_list
        )
        response.append(res_item)
    return response

@router.get(
    "/item/{food_id}",
    response_model=FoodItemResponse,
    summary="Get detailed food item by ID with full vitamin & mineral profile"
)
def get_food_detail(food_id: int, db: Session = Depends(get_db)):
    item = get_food_item_by_id(db, food_id)
    if not item:
        raise HTTPException(status_code=404, detail="Food item not found")
    nutrients = get_food_nutrients(db, item.id)
    nutrient_list = [
        FoodNutrientResponse(
            id=fn.id,
            nutrient_name=fn.nutrient.name,
            nutrient_category=fn.nutrient.category,
            amount_per_100g=fn.amount_per_100g,
            unit=fn.unit,
            percent_daily_value=fn.percent_daily_value
        )
        for fn in nutrients if fn.nutrient
    ]
    return FoodItemResponse(
        id=item.id,
        name=item.name,
        name_te=item.name_te,
        name_hi=item.name_hi,
        scientific_name=item.scientific_name,
        category=item.category,
        calories_kcal=item.calories_kcal,
        protein_g=item.protein_g,
        carbs_g=item.carbs_g,
        fat_g=item.fat_g,
        fiber_g=item.fiber_g,
        glycemic_index=item.glycemic_index,
        description=item.description,
        benefits_summary=item.benefits_summary,
        cautions=item.cautions,
        verified_source=item.verified_source,
        nutrients=nutrient_list
    )

@router.get(
    "/nutrients",
    response_model=List[NutrientResponse],
    summary="List all vitamins, minerals, and RDA reference benchmarks"
)
def list_nutrients(
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    clean_category = str(category) if (category and not hasattr(category, 'default')) else None
    return get_nutrients(db, clean_category)

@router.post(
    "/saved",
    response_model=SavedFoodResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Bookmark a food item to user saved foods"
)
def save_food(
    save_in: SavedFoodCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    food = get_food_item_by_id(db, save_in.food_id)
    if not food:
        raise HTTPException(status_code=404, detail="Food item not found")
    saved = save_food_for_user(db, current_user.id, save_in.food_id, save_in.notes)
    return SavedFoodResponse(
        id=saved.id,
        food_id=food.id,
        food_name=food.name,
        food_name_te=food.name_te,
        food_name_hi=food.name_hi,
        category=food.category,
        calories_kcal=food.calories_kcal,
        protein_g=food.protein_g,
        carbs_g=food.carbs_g,
        fiber_g=food.fiber_g,
        image_url=food.image_url,
        benefits_summary=food.benefits_summary,
        notes=saved.notes,
        saved_at=saved.created_at
    )

@router.get(
    "/saved",
    response_model=List[SavedFoodResponse],
    summary="List all bookmarked foods of current user"
)
def list_saved_foods(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    saved_list = get_saved_foods_by_user(db, current_user.id)
    return [
        SavedFoodResponse(
            id=s.id,
            food_id=s.food_id,
            food_name=s.food_item.name if s.food_item else "Unknown",
            food_name_te=s.food_item.name_te if s.food_item else None,
            food_name_hi=s.food_item.name_hi if s.food_item else None,
            category=s.food_item.category if s.food_item else None,
            calories_kcal=s.food_item.calories_kcal if s.food_item else 0.0,
            protein_g=s.food_item.protein_g if s.food_item else 0.0,
            carbs_g=s.food_item.carbs_g if s.food_item else 0.0,
            fiber_g=s.food_item.fiber_g if s.food_item else 0.0,
            image_url=s.food_item.image_url if s.food_item else None,
            benefits_summary=s.food_item.benefits_summary if s.food_item else None,
            notes=s.notes,
            saved_at=s.created_at
        )
        for s in saved_list
    ]

@router.delete(
    "/saved/{food_id}",
    summary="Remove a food from bookmarks",
    description="Deletes a saved food bookmark for the current user."
)
def delete_saved_food(
    food_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    removed = remove_saved_food(db, current_user.id, food_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Saved food not found")
    return {"status": "removed", "food_id": food_id}


@router.post(
    "/water-intake",
    response_model=WaterIntakeResponse,
    summary="Calculate smart personalized water intake requirements",
    description="Calculates exact daily hydration requirements based on body weight, physical activity, climate, and provides an optimal hydration schedule."
)
def calculate_water_intake(req: WaterIntakeRequest):
    if req.weight_kg <= 0 or req.weight_kg > 300:
        raise HTTPException(status_code=400, detail="Please provide a valid body weight between 10 kg and 300 kg.")
    
    # Scientific baseline: 35ml per kg body weight
    base_ml = round(req.weight_kg * 35)
    
    # Activity adjustment: approx 350ml per 30 minutes of physical activity
    activity_ml = round((max(0, req.activity_minutes) / 30.0) * 350)
    
    # Climate adjustment
    climate_lower = (req.climate or "moderate").lower().strip()
    if climate_lower in ["hot", "very hot", "summer"]:
        climate_ml = 500
    elif climate_lower in ["humid", "tropical"]:
        climate_ml = 400
    elif climate_lower in ["cold", "winter"]:
        climate_ml = 0
    else:
        climate_ml = 250
        
    total_ml = base_ml + activity_ml + climate_ml
    total_liters = round(total_ml / 1000.0, 1)
    total_glasses = round(total_ml / 250.0, 1)
    
    # Hourly schedule
    schedule = [
        HourlyScheduleItem(time_window="07:00 - 08:30", amount_ml=500, glasses=2.0, tip="Morning Kickoff: Wake up internal organs and boost metabolism."),
        HourlyScheduleItem(time_window="10:30 - 11:30", amount_ml=250, glasses=1.0, tip="Mid-Morning: Maintain cognitive focus and steady alertness."),
        HourlyScheduleItem(time_window="12:30", amount_ml=250, glasses=1.0, tip="Pre-Lunch: Drink 30 mins before eating for optimal digestion."),
        HourlyScheduleItem(time_window="14:30 - 16:00", amount_ml=500, glasses=2.0, tip="Afternoon Hydration: Prevent the mid-day energy slump."),
        HourlyScheduleItem(time_window="17:30 - 18:30", amount_ml=500, glasses=2.0, tip="Pre-Evening / Workout: Rehydrate before active evening hours."),
        HourlyScheduleItem(time_window="20:00 - 21:00", amount_ml=250, glasses=1.0, tip="Evening Hydration: Gentle hydration without disrupting sleep.")
    ]
    
    # Multilingual conversational advice
    lang = (req.language or "en").lower().strip()
    if lang.startswith("te"):
        advice = f"మీ శరీర బరువు ({req.weight_kg} కిలోలు) మరియు రోజూ చేసే వ్యాయామం ప్రకారం, మీరు రోజూ కనీసం {total_liters} లీటర్ల నీరు (దాదాపు {int(round(total_glasses))} గ్లాసులు) తాగాలి. ఉదయం నిద్రలేవగానే 2 గ్లాసుల నీరు తాగడం ఆరోగ్యానికి చాలా మంచిది!"
    elif lang.startswith("hi"):
        advice = f"आपके शरीर के वजन ({req.weight_kg} किग्रा) और दैनिक गतिविधि के आधार पर, आपको प्रतिदिन लगभग {total_liters} लीटर पानी (लगभग {int(round(total_glasses))} गिलास) पीना चाहिए। भोजन से 30 मिनट पहले पानी पीना पाचन के लिए सर्वोत्तम है!"
    elif lang.startswith("ta"):
        advice = f"உங்கள் உடல் எடை ({req.weight_kg} கிலோ) அடிப்படையில், தினமும் {total_liters} லிட்டர் தண்ணீர் (சுமார் {int(round(total_glasses))} டம்ளர்கள்) குடிக்க வேண்டும்."
    elif lang.startswith("kn"):
        advice = f"ನಿಮ್ಮ ದೇಹದ ತೂಕದ ({req.weight_kg} ಕೆಜಿ) ಆಧಾರದ ಮೇಲೆ, ನೀವು ದಿನಕ್ಕೆ {total_liters} ಲೀಟರ್ ನೀರು (ಸುಮಾರು {int(round(total_glasses))} ಗ್ಲಾಸ್) ಕುಡಿಯಬೇಕು."
    else:
        advice = f"Based on your body weight of {req.weight_kg} kg and daily activity, your target water intake is {total_liters} Liters (approx {int(round(total_glasses))} glasses) per day. Drinking a glass 30 minutes before meals and 2 glasses upon waking helps optimize digestion and metabolism!"
        
    return WaterIntakeResponse(
        weight_kg=req.weight_kg,
        base_requirement_ml=base_ml,
        activity_adjustment_ml=activity_ml,
        climate_adjustment_ml=climate_ml,
        total_daily_water_ml=total_ml,
        total_daily_water_liters=total_liters,
        total_glasses=total_glasses,
        schedule=schedule,
        conversational_advice=advice,
        language=lang
    )


