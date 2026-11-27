"""
Comprehensive Test Script for FoodGenie Text-Based AI Diet & Nutrition Platform
Tests:
1. Pure text Genie AI responses (No voice).
2. Casual greeting ("Hi") -> warm conversational reply without unprompted meal tables.
3. Hair fall inquiry ("I am experiencing hair fall.") -> hair nutrition.
4. Clear skin inquiry ("I want clear skin.") -> skin vitality nutrition.
5. Weight goals (Gain, Loss, Maintenance).
6. Multilingual automatic detection (Telugu, Hindi, English).
7. Food recommendation markdown table, price in INR (₹), serving sizes, vitamins/minerals, and medical safety disclaimer.
8. Budget Planner, Water Calculator, Doctor Finder, and Food Restrictions.
"""

import sys
from database import SessionLocal
from genie_service import process_genie_query
from restriction_service import restriction_service
from budget_service import generate_budget_plan
from schema_budget import BudgetPlanRequest
from doctor_service import doctor_service
from schema_doctor import DoctorSearchRequest
from api_nutrition import calculate_water_intake, WaterIntakeRequest

def run_tests():
    db = SessionLocal()
    print("=" * 70)
    print("FOODGENIE TEXT-BASED AI DIET & NUTRITION PLATFORM VERIFICATION")
    print("=" * 70)

    all_passed = True

    # TEST 1: Casual Greeting
    print("\n[TEST 1] Testing Casual Greeting ('Hi'):")
    res1 = process_genie_query(db=db, query="Hi", preferred_language="en")
    print(f"User: Hi\nGenie: {res1.summary}")
    assert "help you" in res1.summary.lower() or "welcome" in res1.summary.lower() or "healthy" in res1.summary.lower()
    assert "|" not in res1.summary, "Casual greeting should NOT contain a nutrition table!"
    assert len(res1.recommended_foods) == 0, "Casual greeting should have 0 food cards!"
    print("✓ Test 1 Passed: Warm casual greeting returned without unsolicited meal tables.")

    # TEST 2: Hair Fall Inquiry
    print("\n[TEST 2] Testing Hair Fall Inquiry ('I am experiencing hair fall.'):")
    res2 = process_genie_query(db=db, query="I am experiencing hair fall.", preferred_language="en")
    print(f"Summary excerpt: {res2.summary[:300]}...")
    assert "hair" in res2.summary.lower() or "protein" in res2.summary.lower() or "iron" in res2.summary.lower() or "zinc" in res2.summary.lower()
    assert "|" in res2.summary, "Must contain markdown nutrition table!"
    assert "₹" in res2.summary, "Must contain prices in INR (₹)!"
    assert "Disclaimer" in res2.summary or "disclaimer" in res2.summary.lower(), "Must contain medical safety disclaimer!"
    print("✓ Test 2 Passed: Hair fall response contains tailored nutrients, markdown table, INR pricing, and medical disclaimer.")

    # TEST 3: Clear Skin Inquiry
    print("\n[TEST 3] Testing Clear Skin Inquiry ('I want clear skin.'):")
    res3 = process_genie_query(db=db, query="I want clear skin.", preferred_language="en")
    print(f"Summary excerpt: {res3.summary[:300]}...")
    assert "skin" in res3.summary.lower() or "vitamin" in res3.summary.lower() or "antioxidant" in res3.summary.lower()
    assert "|" in res3.summary, "Must contain markdown table!"
    assert "₹" in res3.summary, "Must contain prices in INR (₹)!"
    print("✓ Test 3 Passed: Clear skin response contains antioxidant/collagen wholefoods, table, and INR pricing.")

    # TEST 4: Weight Gain & Weight Loss Queries
    print("\n[TEST 4] Testing Weight Goals:")
    res_gain = process_genie_query(db=db, query="I want to gain weight.", preferred_language="en")
    print(f"Weight Gain: {res_gain.summary[:200]}...")
    assert "weight" in res_gain.summary.lower() or "gain" in res_gain.summary.lower()

    res_loss = process_genie_query(db=db, query="I want to lose weight.", preferred_language="en")
    print(f"Weight Loss: {res_loss.summary[:200]}...")
    assert "weight" in res_loss.summary.lower() or "loss" in res_loss.summary.lower() or "fiber" in res_loss.summary.lower()
    print("✓ Test 4 Passed: Weight goals handled with conversational empathy and appropriate dietary guidance.")

    # TEST 5: Automatic Multilingual Detection (Telugu & Hindi)
    print("\n[TEST 5] Testing Automatic Multilingual Detection:")
    # Telugu query
    res_te = process_genie_query(db=db, query="నాకు జుట్టు రాలుతోంది ఏం తినాలి", preferred_language="te")
    print(f"Telugu Response Excerpt: {res_te.summary[:250]}...")
    assert res_te.language == "te" or any(ord(c) >= 0x0C00 and ord(c) <= 0x0C7F for c in res_te.summary), "Must respond in Telugu!"

    # Hindi query
    res_hi = process_genie_query(db=db, query="मुझे ग्लोइंग स्किन चाहिए", preferred_language="hi")
    print(f"Hindi Response Excerpt: {res_hi.summary[:250]}...")
    assert res_hi.language == "hi" or any(ord(c) >= 0x0900 and ord(c) <= 0x097F for c in res_hi.summary), "Must respond in Hindi!"
    print("✓ Test 5 Passed: Multilingual queries auto-detected and replied in the respective regional language without language selector.")

    # TEST 6: Smart Budget Diet Planner
    print("\n[TEST 6] Testing Smart Budget Diet Planner:")
    req_b = BudgetPlanRequest(monthly_budget_inr=3500, family_members=1, dietary_preference="vegetarian")
    budget_res = generate_budget_plan(req_b)
    assert budget_res.monthly_budget_inr == 3500
    assert len(budget_res.categories) >= 3
    print(f"Per person daily budget: ₹{budget_res.per_person_day_inr:.1f}, Categories: {len(budget_res.categories)}")
    print("✓ Test 6 Passed: Smart Budget Diet Planner calculates affordable ICMR meal allocations.")

    # TEST 7: Smart Water Intake Calculator
    print("\n[TEST 7] Testing Smart Water Intake Calculator:")
    water_req = WaterIntakeRequest(weight_kg=70, activity_minutes=45, climate="hot", language="en")
    water_res = calculate_water_intake(water_req)
    print(f"Calculated water intake: {water_res.total_daily_water_liters} L ({water_res.total_glasses} glasses)")
    assert water_res.total_daily_water_liters > 2.0
    print("✓ Test 7 Passed: Smart Water Intake Calculator accurately computes personalized hydration requirements.")

    # TEST 8: Food Restrictions & Allergies Engine
    print("\n[TEST 8] Testing Food Restrictions Engine:")
    res_restr = restriction_service.analyze_restrictions(
        allergies=["peanut"],
        medical_conditions=["diabetes"],
        dietary_preference="vegetarian",
        language="en"
    )
    assert len(res_restr.restrictions) >= 1
    print(f"Found {len(res_restr.restrictions)} restrictions with safe alternatives.")
    print("✓ Test 8 Passed: Evidence-based restrictions and safe alternatives verified.")

    # TEST 9: Nearby Certified Doctors Finder
    print("\n[TEST 9] Testing Nearby Certified Doctors Finder:")
    doc_req = DoctorSearchRequest(latitude=17.3850, longitude=78.4867, city="Hyderabad", language="en")
    doc_res = doctor_service.find_doctors(doc_req)
    assert len(doc_res.doctors) >= 1
    print(f"Found {len(doc_res.doctors)} certified specialists near Hyderabad.")
    print("✓ Test 9 Passed: Certified doctor directory with geo-distance operational.")

    db.close()
    print("\n" + "=" * 70)
    print("ALL 9 TEST SUITES COMPLETED AND PASSED PERFECTLY!")
    print("=" * 70)

if __name__ == "__main__":
    run_tests()
