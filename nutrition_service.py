from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from model_nutrition import FoodItem, FoodNutrient, Nutrient
from crud_nutrition import get_food_items
from schema_recommendation import RecommendedFoodItem, MacroBreakdown, NutrientDetail

class NutritionRAGRetriever:
    """
    Retrieves verified nutritional evidence from ICMR-NIN & USDA database.
    Calculates exact per-100g and per-serving values deterministically.
    """

    FOOD_PRICE_CONSUMPTION_GUIDE = {
        "Boiled Whole Eggs": {"price": 14.0, "qty": "2 pieces", "meal_cat": "Breakfast", "how": "Hard boil for 8-9 minutes, sprinkle with cumin and black pepper. Best eaten with breakfast or post-workout."},
        "Native Roasted Peanuts": {"price": 6.0, "qty": "30g", "meal_cat": "Evening Snack", "how": "Lightly dry roasted with skin intact. Ideal mid-morning or evening crunch with jaggery."},
        "Spinach": {"price": 15.0, "qty": "1 medium bunch (150g)", "meal_cat": "Lunch", "how": "Saute lightly with garlic and cold-pressed oil, or cook into dal. Always add a squeeze of fresh lemon juice for iron absorption."},
        "Indian Gooseberry (Amla)": {"price": 8.0, "qty": "2 medium pieces", "meal_cat": "Morning Snack", "how": "Consume raw with rock salt, or extract fresh juice and drink on an empty stomach."},
        "Finger Millet (Ragi)": {"price": 10.0, "qty": "1 bowl porridge / 2 rotis (70g)", "meal_cat": "Breakfast", "how": "Whisk with water or buttermilk as refreshing Ragi Java, or make soft hot rotis."},
        "Whole Green Moong": {"price": 12.0, "qty": "1 bowl sprouted (100g)", "meal_cat": "Breakfast", "how": "Sprout for 24-36 hours, toss with diced cucumbers, tomatoes, and lemon juice."},
        "Moringa Leaves": {"price": 15.0, "qty": "1 bunch (100g)", "meal_cat": "Lunch", "how": "Add to toor dal or stir-fry with roasted gram powder. Do not overcook to preserve bioavailable Vitamin C and iron."},
        "Paneer (Cottage Cheese)": {"price": 32.0, "qty": "100g", "meal_cat": "Dinner", "how": "Pan-toss lightly with turmeric and black pepper, or cube raw into salads and curries."},
        "Fresh Curd (Homemade Yogurt)": {"price": 12.0, "qty": "1 bowl (150g)", "meal_cat": "Lunch", "how": "Consume fresh at room temperature with lunch. Probiotics support nutrient assimilation."},
        "Fresh Guava": {"price": 10.0, "qty": "1 medium fruit", "meal_cat": "Morning Snack", "how": "Eat whole with skin and seeds for rich pectin fiber and 200mg Vitamin C."},
        "White Sesame Seeds (Til)": {"price": 8.0, "qty": "2 tablespoons (20g)", "meal_cat": "Morning Snack", "how": "Dry roast lightly and blend into chutneys or prepare nutritious til laddu with jaggery."},
        "Roasted Bengal Gram (Chana)": {"price": 8.0, "qty": "40g", "meal_cat": "Evening Snack", "how": "Enjoy as an evening crunch with roasted peanuts or sprinkle over vegetable salads."},
        "Red Lentils (Masoor Dal)": {"price": 14.0, "qty": "1 bowl cooked (150g)", "meal_cat": "Lunch", "how": "Boil with onions, tomatoes, and cumin tempering. High bioavailable plant protein."},
        "Toor Dal (Pigeon Pea)": {"price": 16.0, "qty": "1 bowl cooked (150g)", "meal_cat": "Lunch", "how": "Cook into traditional sambar or dal with greens. Pair with rice or rotis."},
        "High-Protein Soya Chunks": {"price": 10.0, "qty": "40g dry weight", "meal_cat": "Dinner", "how": "Boil in salted water for 5 minutes, rinse and squeeze thoroughly, add to curries or pulao."},
        "Sprouted Black Chana (Kala Chana)": {"price": 12.0, "qty": "1 bowl (100g)", "meal_cat": "Evening Snack", "how": "Boil with turmeric and mustard seasoning as sundal or snack on raw sprouts."},
        "Flaxseeds": {"price": 6.0, "qty": "1 tablespoon ground (15g)", "meal_cat": "Breakfast", "how": "Grind freshly and mix into warm oats, ragi java, or sprinkle over curd for plant Omega-3 ALA."},
        "Raw Almonds": {"price": 18.0, "qty": "6-8 soaked pieces", "meal_cat": "Morning Snack", "how": "Soak overnight in water, peel off skin in morning to maximize nutrient absorption."},
        "Walnuts (Akhrot)": {"price": 24.0, "qty": "3-4 halves (20g)", "meal_cat": "Morning Snack", "how": "Soak overnight or consume raw. High plant Omega-3 for brain and vascular health."},
        "Sweet Potato": {"price": 15.0, "qty": "1 medium steamed (150g)", "meal_cat": "Evening Snack", "how": "Steam or roast in skin. Sprinkle with chaat masala and lemon. Rich beta-carotene."},
        "Fresh Carrots": {"price": 12.0, "qty": "2 medium raw (150g)", "meal_cat": "Morning Snack", "how": "Eat raw as salad or lightly steam. Pair with healthy fat like nuts for carotenoid uptake."},
        "Steamed Broccoli": {"price": 28.0, "qty": "1 bowl florets (120g)", "meal_cat": "Dinner", "how": "Steam for 3-4 minutes until bright green. Dress with olive oil and rock salt."},
        "Pumpkin Seeds": {"price": 14.0, "qty": "1 tablespoon (20g)", "meal_cat": "Evening Snack", "how": "Dry roast lightly and chew as an afternoon snack for zinc and magnesium."},
        "Sunflower Seeds": {"price": 12.0, "qty": "1 tablespoon (20g)", "meal_cat": "Evening Snack", "how": "Add to smoothies, curd, or eat dry roasted for Vitamin E alpha-tocopherol."},
        "Chia Seeds / Sabja Seeds": {"price": 14.0, "qty": "1 tablespoon soaked (15g)", "meal_cat": "Breakfast", "how": "Soak in water or coconut water for 15 minutes until gelled. Great for hydration."},
        "Fresh Beetroot": {"price": 12.0, "qty": "1 medium boiled / salad (120g)", "meal_cat": "Lunch", "how": "Grate raw into salads with lemon or roast lightly. Nitrates boost oxygen delivery."},
        "Pomegranate (Anar)": {"price": 30.0, "qty": "1 medium fruit (150g)", "meal_cat": "Morning Snack", "how": "Eat fresh arils directly. Punicalagins provide intense cellular antioxidant defense."},
        "Ripe Papaya": {"price": 18.0, "qty": "1 bowl cubed (150g)", "meal_cat": "Breakfast", "how": "Eat fresh before meals. Papain enzyme assists protein breakdown and skin vitality."},
        "Ripe Red Tomatoes": {"price": 8.0, "qty": "2 medium (120g)", "meal_cat": "Lunch", "how": "Cook into curries or soups with healthy oil to maximize fat-soluble lycopene uptake."},
        "Pearl Millet (Bajra)": {"price": 10.0, "qty": "2 rotis (70g)", "meal_cat": "Dinner", "how": "Knead warm water and prepare hot bajra rotis with garlic chutney or dal in winter."},
        "Foxtail Millet (Korralu)": {"price": 14.0, "qty": "1 cup cooked (150g)", "meal_cat": "Lunch", "how": "Cook like rice (1:2 water) or prepare savory vegetable khichdi."},
        "Whole Grain Brown Rice": {"price": 12.0, "qty": "1 cup cooked (150g)", "meal_cat": "Lunch", "how": "Steam with 1:2.5 water ratio. Retains bran, germ, and slow-release B-complex vitamins."},
        "Fresh Green Peas (Matar)": {"price": 15.0, "qty": "1 small bowl (80g)", "meal_cat": "Lunch", "how": "Lightly steam or add to brown rice pulao and curries for plant protein and zinc."},
        "Black Raisins (Munakka)": {"price": 15.0, "qty": "8-10 soaked pieces", "meal_cat": "Morning Snack", "how": "Soak overnight in water, drink the water and chew the raisins in the morning for iron."},
        "Fresh Coconut Kernel": {"price": 12.0, "qty": "2 slices (30g)", "meal_cat": "Morning Snack", "how": "Eat fresh or grind into chutney. Lauric acid provides clean medium-chain fats."},
        "Rajma (Red Kidney Beans)": {"price": 18.0, "qty": "1 bowl cooked (150g)", "meal_cat": "Lunch", "how": "Soak overnight for 8 hours, pressure cook until soft, pair with brown rice."}
    }

    TOPIC_FOOD_MAP = {
        "hair_health": [
            "Boiled Whole Eggs", "Spinach", "Flaxseeds", "Native Roasted Peanuts", "Indian Gooseberry (Amla)",
            "Pumpkin Seeds", "Raw Almonds", "Walnuts (Akhrot)", "Sprouted Black Chana (Kala Chana)", "Whole Green Moong",
            "Moringa Leaves", "Fresh Curd (Homemade Yogurt)", "Red Lentils (Masoor Dal)", "Sunflower Seeds", "Chia Seeds / Sabja Seeds",
            "White Sesame Seeds (Til)", "Finger Millet (Ragi)", "Fresh Guava", "Steamed Broccoli", "High-Protein Soya Chunks"
        ],
        "skin_nutrition": [
            "Indian Gooseberry (Amla)", "Fresh Guava", "Flaxseeds", "Native Roasted Peanuts", "Spinach",
            "Sweet Potato", "Fresh Carrots", "Ripe Papaya", "Walnuts (Akhrot)", "Sunflower Seeds",
            "Fresh Beetroot", "Pomegranate (Anar)", "Ripe Red Tomatoes", "Raw Almonds", "Chia Seeds / Sabja Seeds",
            "Fresh Curd (Homemade Yogurt)", "Steamed Broccoli", "Moringa Leaves", "Whole Green Moong", "Fresh Coconut Kernel"
        ],
        "iron_rich": [
            "Moringa Leaves", "Spinach", "Whole Green Moong", "White Sesame Seeds (Til)", "Boiled Whole Eggs",
            "Sprouted Black Chana (Kala Chana)", "Red Lentils (Masoor Dal)", "Toor Dal (Pigeon Pea)", "Roasted Bengal Gram (Chana)", "Rajma (Red Kidney Beans)",
            "Pearl Millet (Bajra)", "Finger Millet (Ragi)", "Black Raisins (Munakka)", "Pumpkin Seeds", "Fresh Beetroot",
            "Indian Gooseberry (Amla)", "High-Protein Soya Chunks", "Chia Seeds / Sabja Seeds", "Foxtail Millet (Korralu)", "Fresh Green Peas (Matar)"
        ],
        "vitamin_b12": [
            "Fresh Curd (Homemade Yogurt)", "Paneer (Cottage Cheese)", "Boiled Whole Eggs", "High-Protein Soya Chunks", "Fresh Coconut Kernel",
            "Spinach", "Finger Millet (Ragi)", "Whole Green Moong", "Moringa Leaves", "Raw Almonds",
            "Walnuts (Akhrot)", "Indian Gooseberry (Amla)", "Sprouted Black Chana (Kala Chana)", "Red Lentils (Masoor Dal)", "Toor Dal (Pigeon Pea)",
            "Roasted Bengal Gram (Chana)", "White Sesame Seeds (Til)", "Flaxseeds", "Pumpkin Seeds", "Fresh Guava"
        ],
        "vitamin_c": [
            "Indian Gooseberry (Amla)", "Fresh Guava", "Moringa Leaves", "Spinach", "Steamed Broccoli",
            "Ripe Papaya", "Ripe Red Tomatoes", "Pomegranate (Anar)", "Fresh Green Peas (Matar)", "Whole Green Moong",
            "Sweet Potato", "Fresh Carrots", "Fresh Beetroot", "Boiled Whole Eggs", "White Sesame Seeds (Til)",
            "Roasted Bengal Gram (Chana)", "Finger Millet (Ragi)", "Red Lentils (Masoor Dal)", "Pumpkin Seeds", "Chia Seeds / Sabja Seeds"
        ],
        "vitamin_a": [
            "Fresh Carrots", "Sweet Potato", "Spinach", "Moringa Leaves", "Ripe Papaya",
            "Boiled Whole Eggs", "Ripe Red Tomatoes", "Steamed Broccoli", "Fresh Curd (Homemade Yogurt)", "Indian Gooseberry (Amla)",
            "Fresh Guava", "Whole Green Moong", "Finger Millet (Ragi)", "Rajma (Red Kidney Beans)", "Red Lentils (Masoor Dal)",
            "Pumpkin Seeds", "Sunflower Seeds", "Raw Almonds", "Walnuts (Akhrot)", "Pearl Millet (Bajra)"
        ],
        "calcium_rich": [
            "White Sesame Seeds (Til)", "Finger Millet (Ragi)", "Moringa Leaves", "Paneer (Cottage Cheese)", "Fresh Curd (Homemade Yogurt)",
            "Chia Seeds / Sabja Seeds", "High-Protein Soya Chunks", "Raw Almonds", "Spinach", "Sprouted Black Chana (Kala Chana)",
            "Roasted Bengal Gram (Chana)", "Red Lentils (Masoor Dal)", "Toor Dal (Pigeon Pea)", "Whole Green Moong", "Boiled Whole Eggs",
            "Black Raisins (Munakka)", "Pumpkin Seeds", "Sunflower Seeds", "Steamed Broccoli", "Fresh Coconut Kernel"
        ],
        "protein_rich": [
            "High-Protein Soya Chunks", "Whole Green Moong", "Boiled Whole Eggs", "Paneer (Cottage Cheese)", "Native Roasted Peanuts",
            "Roasted Bengal Gram (Chana)", "Rajma (Red Kidney Beans)", "Sprouted Black Chana (Kala Chana)", "Red Lentils (Masoor Dal)", "Toor Dal (Pigeon Pea)",
            "Raw Almonds", "Pumpkin Seeds", "Sunflower Seeds", "Chia Seeds / Sabja Seeds", "Walnuts (Akhrot)",
            "Fresh Curd (Homemade Yogurt)", "Finger Millet (Ragi)", "Foxtail Millet (Korralu)", "Pearl Millet (Bajra)", "Fresh Green Peas (Matar)"
        ],
        "budget_diet": [
            "Finger Millet (Ragi)", "Whole Green Moong", "Native Roasted Peanuts", "Flaxseeds", "Spinach",
            "Roasted Bengal Gram (Chana)", "Toor Dal (Pigeon Pea)", "Red Lentils (Masoor Dal)", "Moringa Leaves", "Fresh Curd (Homemade Yogurt)",
            "Sprouted Black Chana (Kala Chana)", "Sweet Potato", "Fresh Carrots", "Fresh Guava", "Pearl Millet (Bajra)",
            "Foxtail Millet (Korralu)", "Whole Grain Brown Rice", "High-Protein Soya Chunks", "Fresh Green Peas (Matar)", "Indian Gooseberry (Amla)"
        ],
        "general_nutrition": [
            "Finger Millet (Ragi)", "Whole Green Moong", "Spinach", "Fresh Guava", "Boiled Whole Eggs",
            "Moringa Leaves", "Indian Gooseberry (Amla)", "Native Roasted Peanuts", "White Sesame Seeds (Til)", "Paneer (Cottage Cheese)",
            "Fresh Curd (Homemade Yogurt)", "Raw Almonds", "Sweet Potato", "Rajma (Red Kidney Beans)", "Fresh Carrots",
            "Steamed Broccoli", "Pumpkin Seeds", "High-Protein Soya Chunks", "Whole Grain Brown Rice", "Pomegranate (Anar)"
        ],
        "healthy_eating": [
            "Finger Millet (Ragi)", "Whole Green Moong", "Spinach", "Fresh Guava", "Indian Gooseberry (Amla)",
            "Moringa Leaves", "Boiled Whole Eggs", "Fresh Curd (Homemade Yogurt)", "Sweet Potato", "Fresh Carrots",
            "Steamed Broccoli", "Raw Almonds", "Walnuts (Akhrot)", "Pumpkin Seeds", "Chia Seeds / Sabja Seeds",
            "Sprouted Black Chana (Kala Chana)", "Red Lentils (Masoor Dal)", "Fresh Beetroot", "Pomegranate (Anar)", "High-Protein Soya Chunks"
        ]
    }

    KEYWORD_TOPIC_MAP = {
        # Hair
        "hair": "hair_health", "juttu": "hair_health", "జుట్టు": "hair_health", "కుదుళ్లు": "hair_health",
        "बाल": "hair_health", "बालों": "hair_health", "baal": "hair_health", "koondhal": "hair_health",
        "கூந்தல்": "hair_health", "koodalu": "hair_health", "ಕೂದಲು": "hair_health",
        
        # Skin & Glow
        "skin": "skin_nutrition", "glow": "skin_nutrition", "charmam": "skin_nutrition", "చర్మం": "skin_nutrition",
        "కాంతి": "skin_nutrition", "tvacha": "skin_nutrition", "त्वचा": "skin_nutrition", "चमक": "skin_nutrition",
        "collagen": "skin_nutrition", "தோல்": "skin_nutrition", "charma": "skin_nutrition", "ಚರ್ಮ": "skin_nutrition",
        
        # Iron & Hemoglobin & Blood
        "iron": "iron_rich", "hemoglobin": "iron_rich", "raktham": "iron_rich", "రక్తం": "iron_rich",
        "రక్తహీనత": "iron_rich", "ఐరన్": "iron_rich", "khoon": "iron_rich", "खून": "iron_rich",
        "आयरन": "iron_rich", "anemia": "iron_rich", "raththam": "iron_rich", "இரத்தம்": "iron_rich",
        "raktha": "iron_rich", "ರಕ್ತ": "iron_rich",
        
        # Vitamin B12
        "b12": "vitamin_b12", "cobalamin": "vitamin_b12", "విటమిన్ b12": "vitamin_b12", "विटामिन बी12": "vitamin_b12",
        "నరాలు": "vitamin_b12", "नसें": "vitamin_b12",
        
        # Vitamin C & Immunity
        "vitamin c": "vitamin_c", "vit c": "vitamin_c", "విటమిన్ సి": "vitamin_c", "విటమిన్ c": "vitamin_c",
        "विटामिन सी": "vitamin_c", "రోగనిరోధక": "vitamin_c", "immunity": "vitamin_c", "रोग प्रतिरोधक": "vitamin_c",
        
        # Vitamin A & Eyes
        "vitamin a": "vitamin_a", "eyes": "vitamin_a", "vision": "vitamin_a", "కంటి": "vitamin_a",
        "కళ్ళు": "vitamin_a", "आंखें": "vitamin_a", "दृष्टि": "vitamin_a", "kan": "vitamin_a",
        
        # Calcium & Bones & Teeth
        "calcium": "calcium_rich", "bone": "calcium_rich", "emukalu": "calcium_rich", "ఎముకలు": "calcium_rich",
        "దంతాలు": "calcium_rich", "క్యాల్షియం": "calcium_rich", "हड्डियों": "calcium_rich", "हड्डी": "calcium_rich",
        "दांत": "calcium_rich", "teeth": "calcium_rich", "elumbu": "calcium_rich", "எலும்பு": "calcium_rich",
        "moole": "calcium_rich", "ಮೂಳೆ": "calcium_rich",
        
        # Protein & Muscle
        "protein": "protein_rich", "muscle": "protein_rich", "proteen": "protein_rich", "ప్రోటీన్": "protein_rich",
        "బలం": "protein_rich", "కండరాలు": "protein_rich", "प्रोटीन": "protein_rich", "ताकत": "protein_rich",
        "gym": "protein_rich", "புரதம்": "protein_rich", "ಪ್ರೋಟೀನ್": "protein_rich", "dolu": "protein_rich",
        
        # Budget & Affordable Food
        "budget": "budget_diet", "takkuva karchu": "budget_diet", "తక్కువ ఖర్చు": "budget_diet", "బడ్జెట్": "budget_diet",
        "kam kharch": "budget_diet", "कम खर्च": "budget_diet", "बजट": "budget_diet", "cheap": "budget_diet",
        "affordable": "budget_diet", "விலை குறைவு": "budget_diet", "kadime vechha": "budget_diet"
    }

    @classmethod
    def identify_topic(cls, query: str) -> str:
        q = query.lower()
        for kw, topic in cls.KEYWORD_TOPIC_MAP.items():
            if kw in q:
                return topic
        return "general_nutrition"

    @classmethod
    def retrieve_verified_foods(cls, db: Session, query: str, language: str = "en", limit: int = 20) -> List[RecommendedFoodItem]:
        topic = cls.identify_topic(query)
        target_food_names = cls.TOPIC_FOOD_MAP.get(topic, [])

        results: List[RecommendedFoodItem] = []
        fetched_foods: List[FoodItem] = []

        if target_food_names:
            for name in target_food_names:
                f = db.query(FoodItem).filter(FoodItem.name == name).first()
                if f and f not in fetched_foods:
                    fetched_foods.append(f)

        if len(fetched_foods) < limit:
            # General text search in database
            more_foods = get_food_items(db, query=query[:15], limit=limit)
            for f in more_foods:
                if f not in fetched_foods:
                    fetched_foods.append(f)

        if len(fetched_foods) < limit:
            # Database sweep to ensure at least 20 verified foods are always provided
            all_db_foods = db.query(FoodItem).all()
            for f in all_db_foods:
                if f not in fetched_foods:
                    fetched_foods.append(f)
                if len(fetched_foods) >= limit:
                    break

        for food in fetched_foods[:limit]:
            multiplier = food.serving_weight_g / 100.0

            # 1. Macro calculations per 100g vs per serving (exact math, no invented data)
            macros_100g = MacroBreakdown(
                calories_kcal=round(food.calories_kcal, 1),
                protein_g=round(food.protein_g, 1),
                carbs_g=round(food.carbs_g, 1),
                fat_g=round(food.fat_g, 1),
                fiber_g=round(food.fiber_g, 1)
            )

            macros_serving = MacroBreakdown(
                calories_kcal=round(food.calories_kcal * multiplier, 1),
                protein_g=round(food.protein_g * multiplier, 1),
                carbs_g=round(food.carbs_g * multiplier, 1),
                fat_g=round(food.fat_g * multiplier, 1),
                fiber_g=round(food.fiber_g * multiplier, 1)
            )

            # 2. Vitamins & Minerals breakdown
            vitamins: List[NutrientDetail] = []
            minerals: List[NutrientDetail] = []

            for fn in food.food_nutrients:
                if not fn.nutrient:
                    continue
                
                amt_100g = fn.amount_per_100g
                amt_serving = round(amt_100g * multiplier, 2)
                
                detail = NutrientDetail(
                    name=fn.nutrient.name,
                    category=fn.nutrient.category,
                    amount_per_100g=amt_100g,
                    amount_per_serving=amt_serving,
                    unit=fn.unit,
                    percent_daily_value=fn.percent_daily_value
                )

                if fn.nutrient.category == "vitamin":
                    vitamins.append(detail)
                elif fn.nutrient.category in ["mineral", "essential_fatty_acid"]:
                    minerals.append(detail)

            # 3. Preparation Method in target language
            prep = food.preparation_methods
            if language == "te" and food.preparation_methods_te:
                prep = food.preparation_methods_te
            elif language == "hi" and food.preparation_methods_hi:
                prep = food.preparation_methods_hi

            # 4. Benefits breakdown
            benefits_list = [b.strip() for b in (food.benefits_summary or "").split(",") if b.strip()]

            # 5. Localized food title
            title = food.name
            if language == "te" and food.name_te:
                title = food.name_te
            elif language == "hi" and food.name_hi:
                title = food.name_hi

            guide = cls.FOOD_PRICE_CONSUMPTION_GUIDE.get(
                food.name,
                {"price": 15.0, "qty": "100g", "meal_cat": "Lunch", "how": food.preparation_methods or "Consume fresh as part of a balanced wholefood meal."}
            )
            est_price = guide.get("price", 15.0)
            how_consume = guide.get("how", prep or "Consume as part of a balanced wholefood meal.")
            serving_display = guide.get("qty", food.serving_size or "100g")
            meal_cat = guide.get("meal_cat", "Lunch")

            results.append(
                RecommendedFoodItem(
                    id=food.id,
                    name=title,
                    name_te=food.name_te,
                    name_hi=food.name_hi,
                    image_url=food.image_url,
                    category=food.category,
                    meal_category=meal_cat,
                    serving_size=serving_display,
                    serving_weight_g=food.serving_weight_g or 100.0,
                    estimated_price_inr=est_price,
                    price_type="estimated_market_price",
                    how_to_consume=how_consume,
                    benefit=food.benefits_summary or "Nutrient dense wholefood.",
                    health_benefits=benefits_list,
                    nutrients_per_100g=macros_100g,
                    nutrients_per_serving=macros_serving,
                    vitamins=vitamins,
                    minerals=minerals,
                    preparation_methods=prep,
                    cautions=food.cautions,
                    verified_source=food.verified_source
                )
            )

        return results

nutrition_rag = NutritionRAGRetriever()
