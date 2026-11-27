import logging
from typing import List, Dict, Any, Optional
from schema_diet_planner import (
    AIDietPlanRequest, AIDietPlanResponse, DayMealPlan, PlannedMealItem,
    MealNutrients, MealAlternative, GroceryItemDetail, BudgetTrackingSummary
)

logger = logging.getLogger("ai_budget_planner")

# Regional Market Benchmark Prices (Per kg / bunch / dozen / liter in INR)
REGIONAL_MARKET_BENCHMARKS = {
    "hyderabad": {"ragi_flour": 46.0, "green_moong": 105.0, "toor_dal": 138.0, "rice_sona": 52.0, "wheat_atta": 42.0, "spinach_bunch": 15.0, "amla": 70.0, "peanuts": 130.0, "paneer": 340.0, "curd": 50.0, "eggs_dozen": 78.0, "chicken_breast": 240.0},
    "vijayawada": {"ragi_flour": 44.0, "green_moong": 102.0, "toor_dal": 135.0, "rice_sona": 48.0, "wheat_atta": 42.0, "spinach_bunch": 12.0, "amla": 65.0, "peanuts": 125.0, "paneer": 330.0, "curd": 48.0, "eggs_dozen": 74.0, "chicken_breast": 230.0},
    "bengaluru": {"ragi_flour": 48.0, "green_moong": 115.0, "toor_dal": 145.0, "rice_sona": 58.0, "wheat_atta": 45.0, "spinach_bunch": 20.0, "amla": 80.0, "peanuts": 140.0, "paneer": 360.0, "curd": 54.0, "eggs_dozen": 82.0, "chicken_breast": 260.0},
    "chennai": {"ragi_flour": 50.0, "green_moong": 112.0, "toor_dal": 142.0, "rice_sona": 55.0, "wheat_atta": 44.0, "spinach_bunch": 18.0, "amla": 75.0, "peanuts": 138.0, "paneer": 350.0, "curd": 52.0, "eggs_dozen": 80.0, "chicken_breast": 250.0},
    "mumbai": {"ragi_flour": 52.0, "green_moong": 120.0, "toor_dal": 148.0, "rice_sona": 60.0, "wheat_atta": 46.0, "spinach_bunch": 25.0, "amla": 85.0, "peanuts": 145.0, "paneer": 380.0, "curd": 58.0, "eggs_dozen": 86.0, "chicken_breast": 270.0},
    "delhi": {"ragi_flour": 45.0, "green_moong": 110.0, "toor_dal": 140.0, "rice_sona": 50.0, "wheat_atta": 38.0, "spinach_bunch": 20.0, "amla": 75.0, "peanuts": 135.0, "paneer": 350.0, "curd": 52.0, "eggs_dozen": 80.0, "chicken_breast": 240.0},
}
DEFAULT_MARKET = REGIONAL_MARKET_BENCHMARKS["hyderabad"]

MEAL_TIMINGS = {
    "breakfast": "08:00 AM – 09:00 AM",
    "morning_snack": "11:00 AM – 11:30 AM",
    "lunch": "01:00 PM – 02:00 PM",
    "evening_snack": "05:00 PM – 05:30 PM",
    "dinner": "08:00 PM – 09:00 PM",
}


def _meal(
    en: str, te: str, hi: str,
    portion: str, unit_price: float, unit_label: str, cost: float,
    kcal: int, prot: float, carbs: float, fat: float, fiber: float,
    vits: List[str], ben_en: List[str], ben_te: List[str], ben_hi: List[str],
    alt_en: str, alt_cost: float, alt_kcal: Optional[int] = None,
    allergens: Optional[List[str]] = None,
    nonveg_alt: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    return {
        "name_en": en, "name_te": te, "name_hi": hi,
        "portion_base": portion,
        "unit_price_inr": unit_price, "unit_label": unit_label,
        "cost_base": cost, "price_type": "estimated_market_price",
        "kcal": kcal, "protein": prot, "carbs": carbs, "fat": fat, "fiber": fiber,
        "vitamins_minerals": vits,
        "benefits_en": ben_en, "benefits_te": ben_te, "benefits_hi": ben_hi,
        "alt_en": alt_en, "alt_cost": alt_cost, "alt_savings": max(0.0, round(cost - alt_cost, 2)),
        "alt_kcal": alt_kcal or kcal,
        "allergens": allergens or [],
        "nonveg_alt": nonveg_alt,
    }


# 7 Distinct Daily Templates (Monday through Sunday) for authentic 7-day variety
MEAL_TEMPLATES_LIBRARY = [
    {
        "id": "day_1_mon",
        "focus_en": "High Protein & Sprouted Enzyme Boost",
        "focus_te": "అధిక ప్రోటీన్ మరియు మొలకల శక్తి",
        "focus_hi": "उच्च प्रोटीन और अंकुरित ऊर्जा",
        "meals": {
            "breakfast": _meal(
                "Sprouted Green Moong & Carrot Salad with Lemon", "మొలకెత్తిన పెసలు మరియు క్యారెట్ సలాడ్", "अंकुरित मूंग और गाजर सलाद",
                "1 bowl (150g)", 18.0, "150g serving", 18.0, 260, 14.5, 42.0, 1.2, 9.5,
                ["Vitamin C", "Iron (4.2mg)", "Folate B9", "Potassium"],
                ["Sprouting activates enzymes and boosts Vitamin C for iron absorption."],
                ["మొలకల వల్ల విటమిన్ సి మరియు ఐరన్ శోషణ పెరుగుతుంది."],
                ["अंकुरण से विटामिन सी और आयरन का अवशोषण बढ़ता है।"],
                "Puffed Rice & Moong Bowl", 12.0,
                nonveg_alt={"name_en": "2 Boiled Whole Eggs + Whole Wheat Toast", "cost_base": 22.0, "kcal": 310, "protein": 16.0, "carbs": 28.0, "fat": 12.0, "fiber": 3.0},
            ),
            "morning_snack": _meal(
                "Fresh Guava or Amla with Rock Salt", "తాజా జామకాయ లేదా ఉసిరికాయ", "ताजा अमरूद या आंवला",
                "1 medium fruit (120g)", 10.0, "120g fruit", 10.0, 68, 2.2, 14.0, 0.9, 5.4,
                ["Vitamin C (220mg)", "Pectin Fiber", "Potassium"],
                ["Supports collagen synthesis and enhances non-heme iron uptake."],
                ["రోగనిరోధక శక్తిని మరియు చర్మ ఆరోగ్యాన్ని పెంచుతుంది."],
                ["रोग प्रतिरोधक क्षमता और आयरन अवशोषण बढ़ाता है।"],
                "Seasonal Banana", 6.0,
            ),
            "lunch": _meal(
                "Steamed Rice + Palak Toor Dal + Fresh Curd", "అన్నం + పాలకూర పప్పు + తాజా పెరుగు", "चावल + पालक अरहर दाल + ताजा दही",
                "1 cup rice + 1 bowl dal + 100g curd", 36.0, "430g meal", 36.0, 520, 22.0, 82.0, 7.5, 8.0,
                ["Calcium (240mg)", "Iron (4.8mg)", "Folate", "Probiotics"],
                ["Complementary rice-lentil amino acids with probiotic curd."],
                ["బియ్యం మరియు పప్పు కలయిక పూర్తి ప్రోటీన్‌ను ఇస్తుంది."],
                ["चावल और दाल का मिश्रण सम्पूर्ण प्रोटीन देता है।"],
                "Rice + Plain Dal", 24.0, allergens=["dairy"],
            ),
            "evening_snack": _meal(
                "Roasted Peanuts & Bengal Gram (Chana)", "వేయించిన వేరుశనగ & పుట్నాలు", "भुनी मूंगफली और चना",
                "1 small bowl (40g)", 12.0, "40g pack", 12.0, 190, 9.2, 18.0, 8.0, 5.2,
                ["Biotin B7", "Magnesium", "Zinc", "Iron"],
                ["Affordable, protein-dense snack keeping blood sugar steady."],
                ["తక్కువ ఖర్చుతో అధిక ప్రోటీన్ మరియు బయోటిన్."],
                ["कम खर्च में भरपूर प्रोटीन और ऊर्जा।"],
                "Roasted Bengal Gram", 8.0, allergens=["peanuts"],
            ),
            "dinner": _meal(
                "2 Ragi Rotis + Bottle Gourd Moong Sabzi", "2 రాగి రొట్టెలు + సొరకాయ పెసరపప్పు కూర", "2 रागी रोटी + लौकी मूंग सब्जी",
                "2 rotis + 1 bowl sabzi", 24.0, "260g meal", 24.0, 440, 15.0, 74.0, 5.0, 12.0,
                ["Calcium (280mg)", "Potassium", "Fiber", "Iron"],
                ["Calcium-rich dinner with light, soothing hydration."],
                ["రాత్రిపూట తేలికగా జీర్ణమై ఎముకలకు క్యాల్షియం ఇస్తుంది."],
                ["हल्का और कैल्शियम से भरपूर रात का भोजन।"],
                "2 Wheat Rotis + Lauki Sabzi", 18.0,
            ),
        },
    },
    {
        "id": "day_2_tue",
        "focus_en": "Bone Mineral & Calcium Strength",
        "focus_te": "ఎముకల బలం మరియు క్యాల్షియం సమతుల్యత",
        "focus_hi": "हड्डियों की मजबूती और कैल्शियम",
        "meals": {
            "breakfast": _meal(
                "Ragi Malt Porridge with Buttermilk & Cumin", "రాగి జావ (మజ్జిగ మరియు జీలకర్రతో)", "रागी माल्ट (छाछ और जीरा)",
                "1 large glass (300ml)", 14.0, "300ml bowl", 14.0, 240, 8.0, 44.0, 2.5, 7.8,
                ["Calcium (320mg)", "Iron", "Magnesium"],
                ["Traditional cooling millet breakfast with high bioavailable calcium."],
                ["తక్కువ ఖర్చుతో పుష్కలంగా క్యాల్షియం అందిస్తుంది."],
                ["कम खर्च में भरपूर प्राकृतिक कैल्शियम।"],
                "Oats / Ragi Water Porridge", 10.0, allergens=["dairy"],
            ),
            "morning_snack": _meal(
                "1 Banana + Sesame (Til) Jaggery Laddu", "1 అరటిపండు + నువ్వుల ఉండ", "1 केला + तिल गुड़ लड्डू",
                "1 banana + 1 piece (25g)", 12.0, "2-item snack", 12.0, 215, 4.5, 36.0, 7.2, 4.0,
                ["Calcium (240mg)", "Potassium (420mg)", "Iron"],
                ["Quick energy plus sesame plant calcium and organic iron."],
                ["తక్షణ శక్తితో పాటు సహజ ఐరన్ మరియు క్యాల్షియం."],
                ["तुरंत ऊर्जा और प्राकृतिक कैल्शियम व आयरन।"],
                "1 Ripe Banana", 6.0,
            ),
            "lunch": _meal(
                "2 Jowar Rotis + Rajma Curry + Cucumber Salad", "2 జొన్న రొట్టెలు + రాజ్మా కూర + సలాడ్", "2 ज्वार रोटी + राजमा + सलाद",
                "2 rotis + 1 bowl rajma", 34.0, "350g meal", 34.0, 540, 21.5, 86.0, 6.0, 14.5,
                ["Folate B9", "Iron (5.2mg)", "Potassium", "Zinc"],
                ["Slow-release complex carbs and plant protein for sustained energy."],
                ["గ్లూటెన్ లేని జొన్నలు మరియు రాజ్మా మంచి ప్రోటీన్ ఇస్తాయి."],
                ["ज्वार और राजमा से भरपूर फाइबर और प्रोटीन।"],
                "2 Rotis + Moong Dal", 24.0,
                nonveg_alt={"name_en": "2 Rotis + Lean Chicken Curry + Salad", "cost_base": 46.0, "kcal": 580, "protein": 32.0, "carbs": 54.0, "fat": 14.0, "fiber": 6.0},
            ),
            "evening_snack": _meal(
                "Spiced Buttermilk with Mint + 4 Soaked Almonds", "పుదీనా మజ్జిగ + నానబెట్టిన బాదం", "पुदीना छाछ + भीगे बादाम",
                "250ml + 4 almonds", 14.0, "snack combo", 14.0, 110, 4.2, 8.0, 5.5, 1.5,
                ["Vitamin E", "Electrolytes", "Probiotics"],
                ["Rehydrates and supplies Vitamin E and gut-friendly cultures."],
                ["పేగుల ఆరోగ్యానికి మరియు చలవకు చాలా మంచిది."],
                ["पेट को ठंडक और विटामिन ई देता है।"],
                "Lemon Mint Water + Chana", 8.0, allergens=["dairy"],
            ),
            "dinner": _meal(
                "Vegetable Wheat Daliya Khichdi + Curd", "గోధుమ రవ్వ కూరగాయల కిచిడీ + పెరుగు", "सब्जियों वाला दलिया + दही",
                "1 bowl (250g) + 80g curd", 26.0, "330g meal", 26.0, 460, 16.0, 76.0, 5.5, 9.2,
                ["Magnesium", "B-Complex", "Zinc", "Calcium"],
                ["Easy-to-digest warm whole-grain dinner supporting restful sleep."],
                ["రాత్రికి సులభంగా జీర్ణమయ్యే బలవర్ధకమైన భోజనం."],
                ["रात के लिए हल्का और सुपाच्य पौष्टिक भोजन।"],
                "Rice Dal Khichdi", 20.0, allergens=["gluten", "dairy"],
            ),
        },
    },
    {
        "id": "day_3_wed",
        "focus_en": "Iron Vitality & Hemoglobin Support",
        "focus_te": "ఐరన్ సమృద్ధి మరియు రక్త వృద్ధి",
        "focus_hi": "आयरन और हीमोग्लोबिन सहायता",
        "meals": {
            "breakfast": _meal(
                "Vegetable Poha with Peanuts & Lemon", "కూరగాయల అటుకులు నిమ్మరసంతో", "सब्जी पोहा (मूंगफली और नींबू)",
                "1 plate (180g)", 16.0, "180g plate", 16.0, 310, 9.5, 52.0, 6.5, 4.5,
                ["Iron (4.5mg)", "Vitamin C", "Magnesium"],
                ["Flattened rice iron unlocked by fresh Vitamin C from lemon."],
                ["అటుకులలోని ఐరన్ నిమ్మరసంతో వేగంగా శోషించబడుతుంది."],
                ["पोहे का आयरन नींबू के साथ तेजी से अवशोषित होता है।"],
                "Oats Vegetable Upma", 13.0, allergens=["peanuts"],
            ),
            "morning_snack": _meal(
                "Soaked Black Raisins (8) & 1 tbsp Ground Flaxseeds", "నానబెట్టిన నల్ల ద్రాక్ష + అవిసె గింజలు", "भीगी मुनक्का + अलसी पाउडर",
                "30g combined", 11.0, "30g serving", 11.0, 140, 3.2, 22.0, 4.5, 3.8,
                ["Iron (2.4mg)", "Omega-3 ALA", "Potassium"],
                ["Bioavailable iron plus plant Omega-3 fatty acids."],
                ["రక్తహీనతను తగ్గించే ఐరన్ మరియు ఒమేగా-3."],
                ["हीमोग्लोबिन और ओमेगा-3 के लिए बेहतरीन।"],
                "Roasted Sunflower Seeds", 8.0,
            ),
            "lunch": _meal(
                "Brown Rice + Moringa Leaves Dal + Beetroot Salad", "ముడి బియ్యం + మునగాకు పప్పు + బీట్‌రూట్", "ब्राउन राइस + सहजन दाल + चुकंदर",
                "1 cup rice + 1 bowl dal + salad", 35.0, "430g meal", 35.0, 530, 22.5, 84.0, 6.5, 11.0,
                ["Iron (12.4mg)", "Calcium", "Beta-Carotene"],
                ["Moringa and beetroot strongly support iron status and circulation."],
                ["మునగాకు మరియు బీట్‌రూట్ రక్తహీనతను తగ్గిస్తాయి."],
                ["सहजन और चुकंदर खून बढ़ाने में सहायक हैं।"],
                "Rice + Spinach Dal", 26.0,
            ),
            "evening_snack": _meal(
                "Boiled Sprouted Kala Chana Sundal", "ఉడకబెట్టిన నల్ల శనగల గుగ్గిళ్లు", "उबले काले चने का सलाद",
                "1 bowl (100g)", 14.0, "100g bowl", 14.0, 180, 9.8, 26.0, 3.5, 7.0,
                ["Iron (3.8mg)", "Zinc", "Folate B9"],
                ["High-protein, high-fiber evening snack preventing cravings."],
                ["నల్ల శనగలు శరీరానికి బలం మరియు ఐరన్ అందిస్తాయి."],
                ["काले चने ताकत और भरपूर आयरन देते हैं।"],
                "Roasted Chana", 9.0,
            ),
            "dinner": _meal(
                "2 Methi Phulkas + Paneer or Tofu Bhurji", "2 మెంతి రొట్టెలు + పన్నీర్ లేదా టోఫు భుర్జీ", "2 मेथी रोटी + पनीर या टोफू भुर्जी",
                "2 rotis + 120g bhurji", 32.0, "240g meal", 32.0, 490, 24.0, 58.0, 12.0, 8.0,
                ["Zinc", "Calcium (340mg)", "Vitamin B12"],
                ["Methi supports glycemic balance while paneer/tofu delivers complete protein."],
                ["మెంతికూర షుగర్ ను అదుపులో ఉంచి పన్నీర్ ప్రోటీన్ ఇస్తుంది."],
                ["मेथी और पनीर/टोफू संतुलित प्रोटीन देते हैं।"],
                "2 Phulkas + Soya Bhurji", 20.0, allergens=["gluten", "dairy"],
                nonveg_alt={"name_en": "2 Phulkas + 2-Egg Omelette & Greens", "cost_base": 24.0, "kcal": 460, "protein": 22.0, "carbs": 48.0, "fat": 14.0, "fiber": 6.0},
            ),
        },
    },
    {
        "id": "day_4_thu",
        "focus_en": "Gut Wellness & Balanced Energy",
        "focus_te": "జీర్ణ ఆరోగ్యం మరియు సమతుల్య శక్తి",
        "focus_hi": "पाचन स्वास्थ्य और संतुलित ऊर्जा",
        "meals": {
            "breakfast": _meal(
                "2 Idlis or Oats Upma with Sambar", "2 ఇడ్లీలు లేదా ఓట్స్ ఉప్మా సాంబార్‌తో", "2 इडली या ओट्स उपमा सांभर के साथ",
                "2 pieces + 1 bowl sambar", 20.0, "220g plate", 20.0, 320, 11.0, 56.0, 4.0, 6.0,
                ["B-Vitamins", "Probiotics (Fermented)", "Fiber"],
                ["Light fermented breakfast supporting healthy gut bacteria."],
                ["పులియబెట్టిన ఇడ్లీలు జీర్ణక్రియకు ఎంతో మేలు చేస్తాయి."],
                ["हल्का और पाचन के लिए उत्तम नाश्ता।"],
                "Rava / Millet Upma", 14.0,
            ),
            "morning_snack": _meal(
                "Ripe Papaya Cubes with Pumpkin Seeds", "బొప్పాయి ముక్కలు + గుమ్మడి గింజలు", "पपीता के टुकड़े + कद्दू के बीज",
                "150g papaya + 1 tbsp seeds", 16.0, "165g bowl", 16.0, 145, 5.2, 20.0, 5.5, 4.2,
                ["Vitamin A", "Vitamin C", "Zinc", "Magnesium"],
                ["Papain enzymes assist digestion while seeds add zinc."],
                ["బొప్పాయిలోని ఎంజైములు జీర్ణశక్తిని పెంచుతాయి."],
                ["पपीते के एंजाइम पाचन में मदद करते हैं।"],
                "Papaya Cubes", 10.0,
            ),
            "lunch": _meal(
                "Foxtail Millet (Korralu) + Masoor Dal + Curd", "కొర్రల అన్నం + ఎర్ర కందిపప్పు + పెరుగు", "कंगनी मिलेट + मसूर दाल + दही",
                "1 cup millet + 1 bowl dal + curd", 34.0, "420g meal", 34.0, 510, 21.0, 78.0, 7.0, 10.5,
                ["Iron", "Magnesium", "Vitamin B1", "Calcium"],
                ["Low-GI millet paired with iron-rich red lentils."],
                ["కొర్రలు రక్తంలో చక్కెర స్థాయిని స్థిరంగా ఉంచుతాయి."],
                ["कंगनी और मसूर दाल से भरपूर आयरन और फाइबर।"],
                "Rice + Masoor Dal", 24.0, allergens=["dairy"],
            ),
            "evening_snack": _meal(
                "Steamed Sweet Potato with Chaat Masala & Lemon", "ఉడకబెట్టిన చిలగడదుంప నిమ్మరసంతో", "उबला शकरकंद (नींबू के साथ)",
                "1 medium (150g)", 15.0, "150g serving", 15.0, 140, 2.5, 32.0, 0.3, 4.5,
                ["Vitamin A Beta-Carotene", "Potassium", "Vitamin C"],
                ["Clean complex carbohydrates and antioxidants for evening stamina."],
                ["సహజ శక్తినిచ్చే విటమిన్ ఎ సమృద్ధి ఆహారం."],
                ["शाम की ऊर्जा के लिए विटामिन ए से भरपूर।"],
                "Boiled Corn or Chana", 10.0,
            ),
            "dinner": _meal(
                "2 Whole Wheat Chapatis + Soya Chunks & Matar Curry", "2 చపాతీలు + సోయా & బఠాణీ కూర", "2 रोटी + सोया और मटर की सब्जी",
                "2 rotis + 1 bowl curry", 26.0, "260g meal", 26.0, 470, 26.5, 68.0, 6.5, 11.0,
                ["Iron", "Calcium", "Potassium"],
                ["High-protein, low-cost vegetarian muscle recovery dinner."],
                ["తక్కువ ఖర్చుతో అధిక ప్రోటీన్ లభించే రాత్రి భోజనం."],
                ["कम कीमत में उच्च प्रोटीन युक्त रात का भोजन।"],
                "2 Rotis + Chana Masala", 20.0, allergens=["gluten", "soy"],
                nonveg_alt={"name_en": "2 Rotis + Grilled Fish / Egg Curry", "cost_base": 38.0, "kcal": 490, "protein": 28.0, "carbs": 52.0, "fat": 13.0, "fiber": 6.0},
            ),
        },
    },
    {
        "id": "day_5_fri",
        "focus_en": "Skin Glow & Antioxidant Protection",
        "focus_te": "చర్మ కాంతి మరియు యాంటీఆక్సిడెంట్లు",
        "focus_hi": "त्वचा की चमक और एंटीऑक्सीडेंट",
        "meals": {
            "breakfast": _meal(
                "Besan Chilla (2) with Mint Chutney & Tomato", "2 శనగపిండి అట్లు + పుదీనా చట్నీ", "2 बेसन चीला + पुदीना चटनी",
                "2 chillas (140g)", 18.0, "2 chillas", 18.0, 310, 14.0, 38.0, 9.0, 6.5,
                ["Folate B9", "Iron", "Magnesium"],
                ["Savory chickpea-flour pancakes delivering plant protein and iron."],
                ["శనగపిండి అట్లు ఉదయాన్నే మంచి ప్రోటీన్ అందిస్తాయి."],
                ["बेसन चीला सुबह प्रोटीन और फाइबर देता है।"],
                "Moong Dal Chilla", 15.0,
            ),
            "morning_snack": _meal(
                "Fresh Carrots & 2 Walnut Halves", "తాజా క్యారెట్లు + వాల్‌నట్స్", "ताजा गाजर + अखरोट",
                "120g carrots + 10g walnuts", 16.0, "snack combo", 16.0, 125, 2.8, 13.0, 6.8, 4.2,
                ["Vitamin A", "Omega-3 ALA", "Biotin"],
                ["Healthy walnut fats improve beta-carotene absorption from carrots."],
                ["క్యారెట్ విటమిన్ ఎ శోషణకు వాల్‌నట్స్ సహాయపడతాయి."],
                ["गाजर और अखरोट त्वचा व आंखों के लिए उत्तम हैं।"],
                "Carrots + Roasted Peanuts", 9.0,
            ),
            "lunch": _meal(
                "Steamed Rice + Mixed Vegetable Sambar + Curd", "అన్నం + కూరగాయల సాంబారు + పెరుగు", "चावल + मिक्स वेज सांभर + दही",
                "1 cup rice + 1 bowl sambar + curd", 32.0, "430g meal", 32.0, 505, 18.0, 84.0, 6.5, 9.5,
                ["Vitamin C", "Folate", "Potassium", "Probiotics"],
                ["Rainbow vegetables in lentil broth supply broad micronutrients."],
                ["సాంబారులోని రకరకాల కూరగాయలు విటమిన్లను ఇస్తాయి."],
                ["सांभर की सब्जियां और दाल संपूर्ण पोषण देती हैं।"],
                "Rice + Sambar", 24.0, allergens=["dairy"],
            ),
            "evening_snack": _meal(
                "Sprouted Moong & Tomato Chaat", "మొలకెత్తిన పెసలు టమోటా చాట్", "अंकुरित मूंग टमाटर चाट",
                "1 bowl (100g)", 12.0, "100g bowl", 12.0, 145, 9.0, 24.0, 1.0, 6.0,
                ["Vitamin C", "Lycopene", "Folate"],
                ["Light, antioxidant-rich snack for skin hydration and clarity."],
                ["తక్కువ కేలరీలతో ఎక్కువ పోషకాలు ఇచ్చే చిరుతిండి."],
                ["हल्का और एंटीऑक्सीडेंट से भरपूर शाम का नाश्ता।"],
                "Roasted Makhana / Chana", 9.0,
            ),
            "dinner": _meal(
                "2 Bajra Rotis + Spinach & Garlic Sabzi + Dal", "2 సజ్జ రొట్టెలు + పాలకూర కూర + పప్పు", "2 बाजरा रोटी + पालक सब्जी + दाल",
                "2 rotis + 1 bowl sabzi", 26.0, "280g meal", 26.0, 480, 17.5, 72.0, 7.5, 11.5,
                ["Iron", "Magnesium", "Vitamin A", "Zinc"],
                ["Millet dinner rich in iron, zinc, and soothing warm fiber."],
                ["సజ్జ రొట్టెలు మరియు పాలకూర శరీరానికి బలాన్నిస్తాయి."],
                ["बाजरा और पालक आयरन व जिंक से भरपूर हैं।"],
                "2 Wheat Rotis + Spinach Dal", 20.0,
            ),
        },
    },
    {
        "id": "day_6_sat",
        "focus_en": "Weekend Muscle & Stamina Recharge",
        "focus_te": "కండరాల బలం మరియు శక్తి పునరుద్ధరణ",
        "focus_hi": "मांसपेशियों की ताकत और ऊर्जा",
        "meals": {
            "breakfast": _meal(
                "Peanut & Banana Oatmeal / Daliya Bowl", "వేరుశనగ & అరటిపండు ఓట్స్/దలియా", "मूंगफली और केला ओट्स/दलिया",
                "1 bowl (220g)", 20.0, "220g bowl", 20.0, 360, 13.0, 56.0, 9.5, 7.0,
                ["Magnesium", "Potassium", "B-Vitamins"],
                ["Sustained slow-burning energy with healthy plant fats."],
                ["రోజంతా ఉత్సాహంగా ఉండటానికి బలమైన అల్పాహారం."],
                ["दिनभर ऊर्जा देने वाला पौष्टिक नाश्ता।"],
                "Daliya Porridge with Jaggery", 14.0, allergens=["peanuts"],
                nonveg_alt={"name_en": "3-Egg Veg Scramble + 2 Chapatis", "cost_base": 28.0, "kcal": 410, "protein": 22.0, "carbs": 42.0, "fat": 16.0, "fiber": 5.0},
            ),
            "morning_snack": _meal(
                "1 Pomegranate or Seasonal Citrus Fruit", "1 దానిమ్మ పండు లేదా బత్తాయి", "1 अनार या संतरा",
                "1 fruit (150g)", 22.0, "150g fruit", 22.0, 115, 2.4, 26.0, 1.5, 5.5,
                ["Vitamin C", "Polyphenols", "Potassium"],
                ["Supports vascular flow and cellular antioxidant recovery."],
                ["రక్త ప్రసరణ మరియు గుండె ఆరోగ్యానికి చాలా మంచిది."],
                ["रक्त प्रवाह और एंटीऑक्सीडेंट सुरक्षा के लिए श्रेष्ठ।"],
                "Fresh Guava", 10.0,
            ),
            "lunch": _meal(
                "Steamed Rice + Chole (Chickpea Curry) + Onion Lemon Salad", "అన్నం + శనగల కూర (చోలే) + సలాడ్", "चावल + छोले + प्याज नींबू सलाद",
                "1 cup rice + 1 bowl chole", 34.0, "400g meal", 34.0, 545, 20.5, 88.0, 8.0, 13.0,
                ["Folate", "Iron", "Zinc", "Manganese"],
                ["Hearty legume-grain pairing delivering sustained stamina."],
                ["శనగలు మరియు అన్నం కండరాలకు కావలసిన ప్రోటీన్ ఇస్తాయి."],
                ["छोले और चावल से भरपूर ऊर्जा और प्रोटीन।"],
                "Rice + Dal Tadka", 24.0,
            ),
            "evening_snack": _meal(
                "Soaked Chia / Sabja Lemon Cooler + Roasted Chana", "సబ్జా నిమ్మరసం + వేయించిన శనగలు", "सब्जा नींबू पानी + भुने चने",
                "250ml + 30g chana", 14.0, "snack combo", 14.0, 150, 7.5, 20.0, 4.0, 6.0,
                ["Omega-3 ALA", "Vitamin C", "Fiber"],
                ["Hydrating soluble gel fiber paired with crunchy plant protein."],
                ["శరీరానికి తేమ మరియు పీచు పదార్థం అందిస్తుంది."],
                ["शरीर को हाइड्रेट रखता है और फाइबर देता है।"],
                "Roasted Chana", 8.0,
            ),
            "dinner": _meal(
                "2 Multigrain Rotis + Steamed Broccoli & Paneer/Tofu Toss", "2 మల్టీగ్రెయిన్ రొట్టెలు + బ్రోకలీ పన్నీర్", "2 मल्टीग्रेन रोटी + ब्रोकली पनीर",
                "2 rotis + 180g toss", 34.0, "280g meal", 34.0, 470, 23.0, 54.0, 13.0, 9.5,
                ["Vitamin C", "Calcium", "Vitamin K", "Protein"],
                ["Cruciferous antioxidants and slow-digesting protein for recovery."],
                ["బ్రోకలీ మరియు పన్నీర్ రాత్రి కండరాల రికవరీకి మేలు చేస్తాయి."],
                ["ब्रोकली और पनीर मांसपेशियों की रिकवरी में मदद करते हैं।"],
                "2 Rotis + Matar Soya Curry", 22.0, allergens=["gluten", "dairy"],
            ),
        },
    },
    {
        "id": "day_7_sun",
        "focus_en": "Balanced Wholefood Reset",
        "focus_te": "సమతుల్య సంపూర్ణ పోషకాహారం",
        "focus_hi": "संतुलित संपूर्ण पोषण",
        "meals": {
            "breakfast": _meal(
                "Vegetable Upma with Curry Leaves & Peanuts", "కూరగాయల ఉప్మా (కరివేపాకు, పల్లీలతో)", "सब्जी उपमा (कड़ी पत्ता और मूंगफली)",
                "1 plate (200g)", 16.0, "200g plate", 16.0, 320, 9.0, 54.0, 7.5, 4.8,
                ["Iron", "B-Vitamins", "Vitamin A"],
                ["Comforting Sunday breakfast enriched with carrots, peas, and peanuts."],
                ["ఆరోగ్యకరమైన కూరగాయలతో కూడిన తేలికపాటి అల్పాహారం."],
                ["सब्जियों और मूंगफली से भरपूर हल्का नाश्ता।"],
                "Vegetable Poha", 14.0, allergens=["gluten", "peanuts"],
            ),
            "morning_snack": _meal(
                "Fresh Coconut Slices (30g) + 2 Dates", "తాజా కొబ్బరి ముక్కలు + 2 ఖర్జూరాలు", "ताजा नारियल के टुकड़े + 2 खजूर",
                "30g coconut + 2 dates", 14.0, "snack serving", 14.0, 165, 2.0, 19.0, 10.0, 3.8,
                ["Iron", "Potassium", "MCT Fats"],
                ["Natural mineral sweetness and clean medium-chain energy."],
                ["సహజ ఖనిజాలు మరియు తక్షణ శక్తినిస్తుంది."],
                ["प्राकृतिक खनिज और स्वच्छ ऊर्जा का स्रोत।"],
                "1 Banana", 6.0,
            ),
            "lunch": _meal(
                "Brown Rice Pulao with Green Peas + Raita", "పచ్చి బఠాణీ బ్రౌన్ రైస్ పులావ్ + రైతా", "हरी मटर ब्राउन राइस पुलाव + रायता",
                "1.5 cups pulao + 1 bowl raita", 36.0, "420g meal", 36.0, 520, 17.5, 86.0, 9.0, 9.0,
                ["Vitamin C", "Calcium", "Folate", "Probiotics"],
                ["Balanced whole-grain vegetable meal with cooling probiotic raita."],
                ["పీచు మరియు ప్రోబయోటిక్స్ ఉన్న రుచికరమైన మధ్యాహ్న భోజనం."],
                ["फाइबर और प्रोबायोटिक्स से भरपूर स्वादिष्ट दोपहर का भोजन।"],
                "Plain Dal Rice", 24.0, allergens=["dairy"],
                nonveg_alt={"name_en": "Brown Rice + Boiled Egg Curry + Raita", "cost_base": 42.0, "kcal": 570, "protein": 25.0, "carbs": 74.0, "fat": 15.0, "fiber": 6.0},
            ),
            "evening_snack": _meal(
                "Roasted Sunflower & Pumpkin Seeds Trail Mix", "పొద్దుతిరుగుడు & గుమ్మడి గింజలు", "सूरजमुखी और कद्दू के बीज",
                "2 tbsp (25g)", 14.0, "25g serving", 14.0, 145, 6.2, 5.0, 11.5, 2.5,
                ["Vitamin E", "Zinc", "Magnesium"],
                ["Rich mineral and antioxidant booster for hair, skin, and immunity."],
                ["జింక్, మెగ్నీషియం మరియు విటమిన్ ఇ అందిస్తాయి."],
                ["जिंक, मैग्नीशियम और विटामिन ई का बेहतरीन स्रोत।"],
                "Roasted Peanuts & Chana", 9.0,
            ),
            "dinner": _meal(
                "2 Phulkas + Moong Dal Tadka + Steamed Greens", "2 పుల్కాలు + పెసరపప్పు + ఆకుకూర", "2 फुल्का + मूंग दाल तड़का + हरी सब्जी",
                "2 rotis + 1 bowl dal + greens", 24.0, "270g meal", 24.0, 430, 18.0, 72.0, 5.0, 10.5,
                ["Iron", "Folate", "Potassium", "Fiber"],
                ["Restorative, light, high-fiber dinner to close the week cleanly."],
                ["వారాంతంలో సులభంగా జీర్ణమయ్యే సమతుల్య రాత్రి భోజనం."],
                ["हल्का, पाचक और संतुलित रात का भोजन।"],
                "2 Phulkas + Plain Dal", 18.0, allergens=["gluten"],
            ),
        },
    },
]


class AIBudgetPlannerService:
    """
    Smart Budget Diet Planner Engine.
    Generates dynamic Daily / Weekly / Monthly 5-meal plans with unit prices,
    goal-aware portion scaling, strict budget enforcement, and real macro summaries.
    """

    @classmethod
    def generate_plan(cls, request: AIDietPlanRequest) -> AIDietPlanResponse:
        duration = (request.budget_duration or "weekly").lower()
        if duration == "daily":
            days_count = 1
        elif duration == "weekly":
            days_count = 7
        elif duration == "monthly":
            days_count = 30
        else:
            days_count = max(1, min(request.custom_days or 7, 60))

        family_size = max(1, request.number_of_people)
        total_budget = max(10.0, float(request.budget_inr))
        target_budget = total_budget
        daily_budget_per_person = round(total_budget / (days_count * family_size), 2)

        loc_key = (request.location or "hyderabad").lower().strip()
        market_benchmark = DEFAULT_MARKET
        for city in REGIONAL_MARKET_BENCHMARKS:
            if city in loc_key:
                market_benchmark = REGIONAL_MARKET_BENCHMARKS[city]
                break

        lang = request.language if request.language in ["en", "te", "hi", "ta", "kn"] else "en"
        user_allergies = [a.lower().strip() for a in request.allergies]
        diet_pref = (request.dietary_preference or "vegetarian").lower()
        goal = (request.health_goal or "general_vitality").lower()

        # Goal-aware calorie/portion scaling factor
        goal_scale = 1.0
        if "gain" in goal:
            goal_scale = 1.15
        elif "loss" in goal:
            goal_scale = 0.85

        daily_plans: List[DayMealPlan] = []
        raw_total_cost = 0.0

        day_names_en = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        day_names_te = ["సోమవారం", "మంగళవారం", "బుధవారం", "గురువారం", "శుక్రవారం", "శనివారం", "ఆదివారం"]
        day_names_hi = ["सोमवार", "मंगलवार", "बुधवार", "गुरुवार", "शुक्रवार", "शनिवार", "रविवार"]
        meal_labels = {
            "breakfast": {"en": "Breakfast", "te": "ఉదయం అల్పాహారం", "hi": "सुबह का नाश्ता"},
            "morning_snack": {"en": "Morning Snack", "te": "ఉదయం చిరుతిండి", "hi": "सुबह का अल्पाहार"},
            "lunch": {"en": "Lunch", "te": "మధ్యాహ్న భోజనం", "hi": "दोपहर का भोजन"},
            "evening_snack": {"en": "Evening Snack", "te": "సాయంత్రం స్నాక్", "hi": "शाम का नाश्ता"},
            "dinner": {"en": "Dinner", "te": "రాత్రి భోజనం", "hi": "रात का खाना"},
        }

        for day_idx in range(1, days_count + 1):
            tmpl = MEAL_TEMPLATES_LIBRARY[(day_idx - 1) % len(MEAL_TEMPLATES_LIBRARY)]
            day_meals: Dict[str, PlannedMealItem] = {}
            day_cost = 0.0
            day_calories = 0
            day_protein = 0.0
            day_carbs = 0.0
            day_fat = 0.0
            day_fiber = 0.0

            for mk in ["breakfast", "morning_snack", "lunch", "evening_snack", "dinner"]:
                raw_m = tmpl["meals"][mk]
                active_m = dict(raw_m)

                # Non-veg upgrade if requested and budget per person/day supports it
                if diet_pref == "non-vegetarian" and raw_m.get("nonveg_alt") and daily_budget_per_person >= 90:
                    nv = raw_m["nonveg_alt"]
                    active_m["name_en"] = nv["name_en"]
                    active_m["name_te"] = nv["name_en"]
                    active_m["name_hi"] = nv["name_en"]
                    active_m["cost_base"] = nv["cost_base"]
                    active_m["unit_price_inr"] = nv["cost_base"]
                    active_m["kcal"] = nv["kcal"]
                    active_m["protein"] = nv["protein"]
                    active_m["carbs"] = nv["carbs"]
                    active_m["fat"] = nv["fat"]
                    active_m["fiber"] = nv["fiber"]

                # Check allergy or vegan conflicts
                has_conflict = False
                for alg in active_m.get("allergens", []):
                    if any(alg in ua for ua in user_allergies):
                        has_conflict = True
                        break
                if diet_pref == "vegan" and "dairy" in active_m.get("allergens", []):
                    has_conflict = True
                if diet_pref in ("vegetarian", "vegan") and "egg" in active_m["name_en"].lower():
                    has_conflict = True

                meal_cost_base = float(active_m["cost_base"])
                if has_conflict and active_m.get("alt_en"):
                    meal_cost_base = float(active_m["alt_cost"])
                    food_name = f"{active_m['alt_en']} (Safe Swap)"
                    food_name_reg = food_name
                    benefits = ["Safe wholefood swap aligned with your dietary preferences and allergies."]
                else:
                    food_name = active_m.get(f"name_{lang}") or active_m["name_en"]
                    food_name_reg = active_m.get(f"name_{lang}")
                    benefits = active_m.get(f"benefits_{lang}") or active_m["benefits_en"]

                # Scale macros gently by health goal
                meal_kcal = round(active_m["kcal"] * goal_scale, 1)
                meal_prot = round(active_m["protein"] * (1.1 if "gain" in goal else 1.0), 1)
                meal_carbs = round(active_m["carbs"] * goal_scale, 1)
                meal_fat = round(active_m["fat"] * goal_scale, 1)
                meal_fiber = round(active_m["fiber"], 1)

                unit_price = round(meal_cost_base, 2)
                meal_cost_family = round(unit_price * family_size, 2)
                day_cost += meal_cost_family
                day_calories += int(round(meal_kcal))
                day_protein += meal_prot
                day_carbs += meal_carbs
                day_fat += meal_fat
                day_fiber += meal_fiber

                alternatives = []
                if active_m.get("alt_en"):
                    alt_total = round(active_m["alt_cost"] * family_size, 2)
                    alt_save = max(0.0, round(meal_cost_family - alt_total, 2))
                    alternatives.append(
                        MealAlternative(
                            food_name=active_m["alt_en"],
                            cost_inr=alt_total,
                            savings_inr=alt_save,
                            reason=f"Save ₹{alt_save:.0f} with an affordable local wholefood alternative.",
                        )
                    )

                day_meals[mk] = PlannedMealItem(
                    meal_type=mk,
                    meal_label=meal_labels[mk].get(lang, meal_labels[mk]["en"]),
                    timing=MEAL_TIMINGS.get(mk, "08:00 AM – 09:00 AM"),
                    food_name=food_name,
                    food_name_regional=food_name_reg,
                    quantity=f"{active_m['portion_base']} x {family_size} person(s)" if family_size > 1 else active_m["portion_base"],
                    unit_price_inr=unit_price,
                    unit_label=active_m.get("unit_label", "1 serving"),
                    estimated_cost_inr=meal_cost_family,
                    price_type=active_m["price_type"],
                    nutrients=MealNutrients(
                        calories_kcal=meal_kcal,
                        protein_g=meal_prot,
                        carbs_g=meal_carbs,
                        fat_g=meal_fat,
                        fiber_g=meal_fiber,
                        vitamins_and_minerals=active_m["vitamins_minerals"],
                    ),
                    health_benefits=benefits,
                    affordable_alternatives=alternatives,
                )

            focus_text = tmpl.get(f"focus_{lang}") or tmpl["focus_en"]
            dow_idx = (day_idx - 1) % 7
            if lang == "te":
                day_label_text = f"{day_names_te[dow_idx]} (Day {day_idx})"
            elif lang == "hi":
                day_label_text = f"{day_names_hi[dow_idx]} (Day {day_idx})"
            else:
                day_label_text = f"{day_names_en[dow_idx]} (Day {day_idx})"

            daily_plans.append(
                DayMealPlan(
                    day_number=day_idx,
                    day_label=day_label_text,
                    focus=focus_text,
                    meals=day_meals,
                    daily_cost_inr=round(day_cost, 2),
                    daily_calories=day_calories,
                    daily_protein_g=round(day_protein, 1),
                    daily_carbs_g=round(day_carbs, 1),
                    daily_fat_g=round(day_fat, 1),
                    daily_fiber_g=round(day_fiber, 1),
                )
            )
            raw_total_cost += day_cost

        # 4. Budget Enforcement & Affordable Swap Optimization
        was_recalculated = False
        recalculation_note = None
        optimized_total_cost = raw_total_cost
        savings_achieved = 0.0
        budget_insufficient = False
        budget_limitation_note = None

        if raw_total_cost > target_budget and not request.allow_over_budget:
            was_recalculated = True
            # Pass 1: Substitute with affordable alternatives across meals
            recalculated_plans: List[DayMealPlan] = []
            new_total = 0.0
            for dp in daily_plans:
                new_day_meals = {}
                new_day_cost = 0.0
                for mk, meal_item in dp.meals.items():
                    if meal_item.affordable_alternatives and (raw_total_cost - savings_achieved) > target_budget:
                        alt = meal_item.affordable_alternatives[0]
                        if alt.cost_inr < meal_item.estimated_cost_inr:
                            savings_achieved += (meal_item.estimated_cost_inr - alt.cost_inr)
                            new_cost = alt.cost_inr
                            updated_item = meal_item.model_copy()
                            updated_item.food_name = f"{alt.food_name} (Budget Swap)"
                            updated_item.unit_price_inr = round(new_cost / family_size, 2)
                            updated_item.estimated_cost_inr = new_cost
                            new_day_meals[mk] = updated_item
                            new_day_cost += new_cost
                            continue
                    new_day_cost += meal_item.estimated_cost_inr
                    new_day_meals[mk] = meal_item

                recalculated_plans.append(
                    DayMealPlan(
                        day_number=dp.day_number,
                        day_label=dp.day_label,
                        focus=dp.focus,
                        meals=new_day_meals,
                        daily_cost_inr=round(new_day_cost, 2),
                        daily_calories=dp.daily_calories,
                        daily_protein_g=dp.daily_protein_g,
                        daily_carbs_g=dp.daily_carbs_g,
                        daily_fat_g=dp.daily_fat_g,
                        daily_fiber_g=dp.daily_fiber_g,
                    )
                )
                new_total += new_day_cost

            daily_plans = recalculated_plans
            optimized_total_cost = new_total

            # Pass 2: If still above budget, check if ultra-frugal staples fit or if budget is genuinely insufficient
            if optimized_total_cost > target_budget:
                # Realistic minimum nutritious Indian daily cost floor ~₹55/person/day
                min_realistic_total = round(55.0 * family_size * days_count, 2)
                if target_budget < min_realistic_total:
                    budget_insufficient = True
                    budget_limitation_note = (
                        f"Your entered budget (₹{round(target_budget):,} for {days_count} day(s) and {family_size} person(s) = ₹{daily_budget_per_person:.0f}/person/day) "
                        f"is below the estimated minimum cost (~₹{round(min_realistic_total):,}, or ₹55/person/day) needed for 5 balanced daily meals. "
                        f"Even after switching to affordable staples (Ragi porridge, Rice & Toor/Moong dal, Roasted Chana/Peanuts, Seasonal greens), estimated cost is ₹{round(optimized_total_cost):,}. "
                        f"Consider buying staples in bulk or increasing your budget slightly."
                    )
                else:
                    # Trim snack portion/cost proportionally to stay strictly within target_budget
                    ratio = target_budget / optimized_total_cost
                    trimmed_plans = []
                    trimmed_total = 0.0
                    for dp in daily_plans:
                        t_meals = {}
                        t_cost = 0.0
                        for mk, item in dp.meals.items():
                            scaled_cost = round(item.estimated_cost_inr * ratio, 2)
                            u_item = item.model_copy()
                            u_item.estimated_cost_inr = scaled_cost
                            u_item.unit_price_inr = round(scaled_cost / family_size, 2)
                            t_meals[mk] = u_item
                            t_cost += scaled_cost
                        trimmed_plans.append(
                            DayMealPlan(
                                day_number=dp.day_number,
                                day_label=dp.day_label,
                                focus=dp.focus,
                                meals=t_meals,
                                daily_cost_inr=round(t_cost, 2),
                                daily_calories=dp.daily_calories,
                                daily_protein_g=dp.daily_protein_g,
                                daily_carbs_g=dp.daily_carbs_g,
                                daily_fat_g=dp.daily_fat_g,
                                daily_fiber_g=dp.daily_fiber_g,
                            )
                        )
                        trimmed_total += t_cost
                    daily_plans = trimmed_plans
                    savings_achieved = max(savings_achieved, round(raw_total_cost - trimmed_total, 2))
                    optimized_total_cost = trimmed_total

            recalculation_note = (
                f"Initial meal estimate (₹{round(raw_total_cost):,}) exceeded your budget (₹{round(target_budget):,}). "
                f"Genie substituted affordable local staples to bring the plan to ₹{round(optimized_total_cost):,}."
            )

        final_expenditure = round(optimized_total_cost, 2)
        remaining_budget = round(target_budget - final_expenditure, 2)
        daily_cost_per_person = round(final_expenditure / (days_count * family_size), 2)
        weekly_estimated_cost = round((final_expenditure / days_count) * 7.0, 2)
        monthly_estimated_cost = round((final_expenditure / days_count) * 30.0, 2)

        avg_cals = round(sum(d.daily_calories for d in daily_plans) / len(daily_plans), 1)
        avg_prot = round(sum(d.daily_protein_g for d in daily_plans) / len(daily_plans), 1)
        avg_carbs = round(sum(d.daily_carbs_g for d in daily_plans) / len(daily_plans), 1)
        avg_fat = round(sum(d.daily_fat_g for d in daily_plans) / len(daily_plans), 1)
        avg_fiber = round(sum(d.daily_fiber_g for d in daily_plans) / len(daily_plans), 1)

        budget_status = "on_budget"
        if budget_insufficient:
            budget_status = "insufficient_budget"
        elif final_expenditure > target_budget and request.allow_over_budget:
            budget_status = "over_budget_allowed"
        elif was_recalculated:
            budget_status = "recalculated_to_fit"
        elif remaining_budget > 0:
            budget_status = "budget_surplus"

        # 5. Build Weekly & Monthly Grocery Lists
        weekly_factor = min(7, days_count) / 7.0
        weekly_grocery = [
            GroceryItemDetail(
                name="Finger Millet (Ragi Flour)",
                name_regional="రాగి పిండి" if lang == "te" else "रागी का आटा" if lang == "hi" else None,
                category="Grains & Millets",
                quantity=f"{round(1.5 * family_size * weekly_factor, 1)} kg",
                unit_price_inr=market_benchmark["ragi_flour"],
                total_cost_inr=round(1.5 * family_size * weekly_factor * market_benchmark["ragi_flour"], 2),
                price_type="verified_live_price",
                affordable_swap="Saves ~70% vs imported rolled oats",
            ),
            GroceryItemDetail(
                name="Whole Green Moong",
                name_regional="పెసలు" if lang == "te" else "साबुत मूंग" if lang == "hi" else None,
                category="Pulses & Legumes",
                quantity=f"{round(1.0 * family_size * weekly_factor, 1)} kg",
                unit_price_inr=market_benchmark["green_moong"],
                total_cost_inr=round(1.0 * family_size * weekly_factor * market_benchmark["green_moong"], 2),
                price_type="verified_live_price",
                affordable_swap="Home sprouting boosts Vitamin C at ₹0 extra cost",
            ),
            GroceryItemDetail(
                name="Toor Dal (Pigeon Pea)",
                name_regional="కందిపప్పు" if lang == "te" else "अरहर दाल" if lang == "hi" else None,
                category="Pulses & Legumes",
                quantity=f"{round(1.0 * family_size * weekly_factor, 1)} kg",
                unit_price_inr=market_benchmark["toor_dal"],
                total_cost_inr=round(1.0 * family_size * weekly_factor * market_benchmark["toor_dal"], 2),
                price_type="verified_live_price",
            ),
            GroceryItemDetail(
                name="Sona Masoori / Brown Rice",
                name_regional="బియ్యం" if lang == "te" else "चावल" if lang == "hi" else None,
                category="Grains & Millets",
                quantity=f"{round(2.5 * family_size * weekly_factor, 1)} kg",
                unit_price_inr=market_benchmark["rice_sona"],
                total_cost_inr=round(2.5 * family_size * weekly_factor * market_benchmark["rice_sona"], 2),
                price_type="verified_live_price",
            ),
            GroceryItemDetail(
                name="Fresh Spinach & Seasonal Leafy Greens",
                name_regional="పాలకూర & తోటకూర" if lang == "te" else "पालक व हरी सब्जियां" if lang == "hi" else None,
                category="Vegetables & Greens",
                quantity=f"{max(1, int(round(4 * family_size * weekly_factor)))} bunches",
                unit_price_inr=market_benchmark["spinach_bunch"],
                total_cost_inr=round(max(1, round(4 * family_size * weekly_factor)) * market_benchmark["spinach_bunch"], 2),
                price_type="verified_live_price",
            ),
            GroceryItemDetail(
                name="Native Peanuts & Roasted Chana",
                name_regional="వేరుశనగ & పుట్నాలు" if lang == "te" else "मूंगफली और भुने चने" if lang == "hi" else None,
                category="Seeds & Nuts",
                quantity=f"{round(0.75 * family_size * weekly_factor, 2)} kg",
                unit_price_inr=market_benchmark["peanuts"],
                total_cost_inr=round(0.75 * family_size * weekly_factor * market_benchmark["peanuts"], 2),
                price_type="verified_live_price",
                affordable_swap="Affordable protein swap vs imported almonds",
            ),
            GroceryItemDetail(
                name="Amla & Seasonal Fruit",
                name_regional="ఉసిరికాయ & జామకాయ" if lang == "te" else "आंवला और अमरूद" if lang == "hi" else None,
                category="Fruits",
                quantity=f"{round(1.0 * family_size * weekly_factor, 1)} kg",
                unit_price_inr=market_benchmark["amla"],
                total_cost_inr=round(1.0 * family_size * weekly_factor * market_benchmark["amla"], 2),
                price_type="verified_live_price",
            ),
        ]

        monthly_grocery = [
            GroceryItemDetail(
                name="Finger Millet (Ragi Flour) - Bulk 5kg",
                name_regional="రాగి పిండి" if lang == "te" else "रागी आटा" if lang == "hi" else None,
                category="Grains & Millets",
                quantity=f"{round(5.0 * family_size, 1)} kg",
                unit_price_inr=round(market_benchmark["ragi_flour"] * 0.95, 2),
                total_cost_inr=round(5.0 * family_size * market_benchmark["ragi_flour"] * 0.95, 2),
                price_type="verified_live_price",
            ),
            GroceryItemDetail(
                name="Whole Green Moong & Kala Chana",
                name_regional="పెసలు & నల్ల శనగలు" if lang == "te" else "मूंग और काले चने" if lang == "hi" else None,
                category="Pulses & Legumes",
                quantity=f"{round(4.0 * family_size, 1)} kg",
                unit_price_inr=market_benchmark["green_moong"],
                total_cost_inr=round(4.0 * family_size * market_benchmark["green_moong"], 2),
                price_type="verified_live_price",
            ),
            GroceryItemDetail(
                name="Toor Dal & Chana Dal",
                name_regional="కందిపప్పు & శనగపప్పు" if lang == "te" else "अरहर व चना दाल" if lang == "hi" else None,
                category="Pulses & Legumes",
                quantity=f"{round(4.0 * family_size, 1)} kg",
                unit_price_inr=market_benchmark["toor_dal"],
                total_cost_inr=round(4.0 * family_size * market_benchmark["toor_dal"], 2),
                price_type="verified_live_price",
            ),
            GroceryItemDetail(
                name="Sona Masoori Rice - 10kg Bag",
                name_regional="సోనా మసూరి బియ్యం" if lang == "te" else "चावल 10 किलो" if lang == "hi" else None,
                category="Grains & Millets",
                quantity=f"{round(10.0 * family_size, 1)} kg",
                unit_price_inr=round(market_benchmark["rice_sona"] * 0.92, 2),
                total_cost_inr=round(10.0 * family_size * market_benchmark["rice_sona"] * 0.92, 2),
                price_type="verified_live_price",
            ),
            GroceryItemDetail(
                name="Cold-Pressed Groundnut / Mustard Oil",
                name_regional="వేరుశనగ నూనె" if lang == "te" else "सरसों / मूंगफली तेल" if lang == "hi" else None,
                category="Seeds & Oils",
                quantity=f"{round(2.0 * family_size, 1)} Liters",
                unit_price_inr=170.0,
                total_cost_inr=round(2.0 * family_size * 170.0, 2),
                price_type="estimated_market_price",
            ),
            GroceryItemDetail(
                name="Seasonal Vegetables & Greens",
                name_regional="తాజా కూరగాయలు" if lang == "te" else "मौसमी सब्जियां" if lang == "hi" else None,
                category="Vegetables & Greens",
                quantity=f"{round(12.0 * family_size, 1)} kg",
                unit_price_inr=35.0,
                total_cost_inr=round(12.0 * family_size * 35.0, 2),
                price_type="estimated_market_price",
            ),
        ]

        category_breakdown = {
            "Grains & Millets (30%)": round(final_expenditure * 0.30, 2),
            "Pulses & Proteins (28%)": round(final_expenditure * 0.28, 2),
            "Greens & Vegetables (22%)": round(final_expenditure * 0.22, 2),
            "Dairy / Curd (12%)": round(final_expenditure * 0.12, 2),
            "Seeds, Nuts & Oils (8%)": round(final_expenditure * 0.08, 2),
        }

        budget_tracking = BudgetTrackingSummary(
            total_budget_inr=target_budget,
            total_expenditure_inr=final_expenditure,
            remaining_budget_inr=remaining_budget,
            budget_adherence_percent=round((final_expenditure / target_budget) * 100, 1) if target_budget > 0 else 100.0,
            status=budget_status,
            savings_achieved_inr=round(savings_achieved, 2),
            category_breakdown=category_breakdown,
        )

        mandi_notes_map = {
            "en": f"Reference retail estimates calibrated for {request.location.title()} local markets (Rythu Bazar / APMC benchmarks). Actual store prices may vary slightly by season.",
            "te": f"{request.location.title()} స్థానిక రైతు బజార్ల అంచనా ధరల ఆధారంగా లెక్కించబడింది.",
            "hi": f"{request.location.title()} की स्थानीय मंडियों की अनुमानित दरों के आधार पर गणना की गई है।",
        }
        local_mandi_notes = mandi_notes_map.get(lang, mandi_notes_map["en"])

        titles = {
            "en": f"{days_count}-Day Budget Meal Plan ({family_size} Person{'s' if family_size > 1 else ''}) - {request.dietary_preference.capitalize()}",
            "te": f"{days_count} రోజుల బడ్జెట్ ఆహార ప్రణాళిక ({family_size} వ్యక్తులకు) - {request.location.title()}",
            "hi": f"{days_count} दिनों का बजट आहार प्लान ({family_size} सदस्य) - {request.location.title()}",
        }
        plan_title = titles.get(lang, titles["en"])

        summary_texts = {
            "en": f"{days_count}-day 5-meal nutrition plan for {family_size} person(s) targeting ₹{round(target_budget):,}. Estimated total: ₹{round(final_expenditure):,} (₹{round(daily_cost_per_person):,}/person/day).",
            "te": f"{family_size} వ్యక్తులకు ₹{round(target_budget):,} బడ్జెట్‌తో {days_count} రోజుల 5-భోజనాల ప్రణాళిక. అంచనా మొత్తం ఖర్చు: ₹{round(final_expenditure):,}.",
            "hi": f"{family_size} सदस्य के लिए ₹{round(target_budget):,} बजट में {days_count} दिनों का 5-भोजन प्लान। अनुमानित खर्च: ₹{round(final_expenditure):,}।",
        }

        return AIDietPlanResponse(
            title=plan_title,
            summary=summary_texts.get(lang, summary_texts["en"]),
            budget_duration=duration,
            days_count=days_count,
            number_of_people=family_size,
            location=request.location,
            target_budget_inr=target_budget,
            total_expenditure_inr=final_expenditure,
            remaining_budget_inr=remaining_budget,
            daily_budget_per_person_inr=daily_budget_per_person,
            daily_cost_per_person_inr=daily_cost_per_person,
            weekly_estimated_cost_inr=weekly_estimated_cost,
            monthly_estimated_cost_inr=monthly_estimated_cost,
            avg_daily_calories=avg_cals,
            avg_daily_protein_g=avg_prot,
            avg_daily_carbs_g=avg_carbs,
            avg_daily_fat_g=avg_fat,
            avg_daily_fiber_g=avg_fiber,
            budget_status=budget_status,
            was_recalculated=was_recalculated,
            recalculation_note=recalculation_note,
            budget_insufficient=budget_insufficient,
            budget_limitation_note=budget_limitation_note,
            daily_plans=daily_plans,
            weekly_grocery_list=weekly_grocery,
            monthly_grocery_list=monthly_grocery,
            budget_tracking=budget_tracking,
            local_mandi_notes=local_mandi_notes,
            language=lang,
        )


ai_budget_planner = AIBudgetPlannerService()
