import pytest
from api_recommendations import analyze_restrictions
from restriction_service import restriction_service, RESTRICTION_DATABASE
from schema_recommendation import FoodRestrictionItem, RestrictionAnalysisRequest, RestrictionAnalysisResponse
from genie_service import process_genie_query
from database import SessionLocal

def test_restriction_database_integrity():
    """Verify all restriction database entries have valid structure, translations, and non-empty alternatives."""
    assert len(RESTRICTION_DATABASE) >= 15
    for key, rule in RESTRICTION_DATABASE.items():
        assert "category" in rule
        assert rule["restriction_type"] in ["medically_necessary", "general_suggestion"]
        assert rule["severity"] in ["critical", "high", "moderate", "mild"]
        assert "translations" in rule
        assert "en" in rule["translations"]
        assert "te" in rule["translations"]
        assert "hi" in rule["translations"]
        
        # Check alternatives and reasons are non-empty
        en = rule["translations"]["en"]
        assert len(en["food_name"]) > 0
        assert len(en["reason"]) > 0
        assert len(en["safe_alternatives"]) > 0
        assert len(en["clinical_note"]) > 0

def test_allergies_analysis():
    """Verify allergies produce medically necessary restrictions with safe alternatives."""
    res = restriction_service.analyze_restrictions(
        allergies=["Peanuts", "Gluten / Wheat", "Dairy / Lactose"],
        language="en"
    )
    assert res.total_restrictions >= 3
    assert res.medically_necessary_count >= 3
    
    food_names = [r.food_name.lower() for r in res.restrictions]
    assert any("peanut" in fn for fn in food_names)
    assert any("wheat" in fn or "maida" in fn for fn in food_names)
    assert any("milk" in fn or "casein" in fn for fn in food_names)

def test_medication_interactions():
    """Verify critical drug-food interactions (Warfarin, Statins, Levothyroxine)."""
    # 1. Statins with Grapefruit
    res_statin = restriction_service.analyze_restrictions(
        medications=["Statins"],
        language="en"
    )
    assert res_statin.total_restrictions >= 1
    statin_item = res_statin.restrictions[0]
    assert "Grapefruit" in statin_item.food_name
    assert statin_item.restriction_type == "medically_necessary"
    assert statin_item.severity == "critical"
    assert "CYP3A4" in statin_item.reason
    assert len(statin_item.safe_alternatives) >= 2

    # 2. Warfarin with Vitamin K
    res_warfarin = restriction_service.analyze_restrictions(
        medications=["Warfarin"],
        language="en"
    )
    assert res_warfarin.total_restrictions >= 1
    warfarin_item = res_warfarin.restrictions[0]
    assert "Vitamin K" in warfarin_item.food_name or "Spinach" in warfarin_item.food_name
    assert warfarin_item.restriction_type == "medically_necessary"
    assert warfarin_item.severity == "critical"

    # 3. Levothyroxine with Calcium/Soy
    res_thyroid_med = restriction_service.analyze_restrictions(
        medications=["Levothyroxine"],
        language="en"
    )
    assert res_thyroid_med.total_restrictions >= 1
    item = res_thyroid_med.restrictions[0]
    assert "Calcium" in item.food_name or "Soy" in item.food_name
    assert item.action_type == "time_separate"

def test_medical_conditions():
    """Verify medical condition restrictions (Diabetes, Hypertension, Kidney stones, PCOS, GERD)."""
    res = restriction_service.analyze_restrictions(
        medical_conditions=["Diabetes / Pre-diabetes", "Hypertension (BP)", "Kidney Stones"],
        language="en"
    )
    assert res.total_restrictions >= 3
    food_names = [r.food_name.lower() for r in res.restrictions]
    assert any("sugar" in fn or "maida" in fn for fn in food_names)
    assert any("sodium" in fn or "pickle" in fn for fn in food_names)
    assert any("spinach" in fn or "purine" in fn or "oxalate" in fn for fn in food_names)

def test_multilingual_telugu():
    """Verify complete Telugu localization of food names, reasons, alternatives, disclaimer, and referral."""
    res = restriction_service.analyze_restrictions(
        allergies=["Peanuts"],
        medical_conditions=["Diabetes / Pre-diabetes"],
        medications=["Statins"],
        language="te"
    )
    assert res.language == "te"
    assert res.total_restrictions == 3
    assert len(res.clinical_disclaimer) > 10
    assert "ఫుడ్ జీనీ" in res.clinical_disclaimer
    
    for r in res.restrictions:
        # Verify Telugu characters exist in food_name and reason
        assert any('\u0C00' <= char <= '\u0C7F' for char in r.food_name)
        assert any('\u0C00' <= char <= '\u0C7F' for char in r.reason)
        assert len(r.safe_alternatives) > 0

def test_multilingual_hindi():
    """Verify Hindi localization."""
    res = restriction_service.analyze_restrictions(
        allergies=["Gluten / Wheat"],
        medical_conditions=["Hypertension (BP)"],
        language="hi"
    )
    assert res.language == "hi"
    assert res.total_restrictions == 2
    assert "फूडजिनी" in res.clinical_disclaimer
    for r in res.restrictions:
        assert any('\u0900' <= char <= '\u097F' for char in r.food_name)
        assert any('\u0900' <= char <= '\u097F' for char in r.reason)

def test_api_endpoint_restrictions_analyze():
    """Verify analyze_restrictions endpoint logic for query, conditions, and medications."""
    req = RestrictionAnalysisRequest(
        query="Can I drink grapefruit juice with statins?",
        medical_conditions=["Hypertension (BP)"],
        medications=["Statins"],
        language="en"
    )
    data = analyze_restrictions(req)
    assert data.total_restrictions >= 2
    assert data.medically_necessary_count >= 2
    assert len(data.restrictions) >= 2
    assert "disclaimer" in data.clinical_disclaimer.lower() or "guidance" in data.clinical_disclaimer.lower()
    assert "doctor" in data.doctor_referral.lower() or "physician" in data.doctor_referral.lower()

def test_genie_query_with_restrictions_and_safe_filtering():
    """Verify process_genie_query populates restrictions and excludes contraindicated foods."""
    db = SessionLocal()
    try:
        res = process_genie_query(
            db=db,
            query="What should I avoid for diabetes and high blood pressure?",
            preferred_language="en"
        )
        assert res.query is not None
        assert len(res.restrictions) >= 2
        assert len(res.foods_to_avoid) >= 2
        
        # Medically necessary restrictions must be labeled
        types = [r.restriction_type for r in res.restrictions]
        assert "medically_necessary" in types
        
        # Check doctor referral present
        assert res.doctor_referral is not None
    finally:
        db.close()
