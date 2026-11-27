import pytest
from doctor_service import (
    DoctorFinderService, find_nearby_doctors, calculate_haversine_distance,
    SPECIALIZATIONS_MASTER, VERIFIED_CLINICAL_DIRECTORY, CITY_COORDINATES
)
from schema_doctor import DoctorSearchRequest, DoctorSearchResponse
from api_doctors import search_doctors, search_doctors_get, get_specializations

def test_specializations_catalog_integrity():
    """Verify that all 5 clinical specializations are properly cataloged with multilingual support."""
    expected_codes = {"general_physician", "dermatologist", "dietitian", "gastroenterologist", "endocrinologist"}
    catalog_codes = {s["code"] for s in SPECIALIZATIONS_MASTER}
    assert expected_codes.issubset(catalog_codes)

    specs = DoctorFinderService.get_specializations(lang="en")
    assert len(specs) >= 5
    for s in specs:
        assert s.code in expected_codes
        assert s.label is not None
        assert len(s.focus_areas) >= 2
        assert s.clinical_description is not None

    # Test Telugu localized catalog
    te_specs = DoctorFinderService.get_specializations(lang="te")
    for s in te_specs:
        assert s.label_regional is not None

def test_verified_clinical_directory_integrity():
    """Verify that clinical directory has verified details for all 5 specializations without fake data."""
    assert len(VERIFIED_CLINICAL_DIRECTORY) >= 10
    spec_counts = {}
    for doc in VERIFIED_CLINICAL_DIRECTORY:
        assert doc["id"].startswith("doc-")
        assert doc["name"]
        assert doc["experience_years"] > 0
        assert doc["clinic_or_hospital"]
        assert doc["address"]
        assert doc["city"]
        assert doc["latitude"] != 0
        assert doc["longitude"] != 0
        assert doc["consultation_fee_inr"] > 0
        assert len(doc["available_days"]) > 0
        assert doc["contact_phone"].startswith("+91")
        assert "accreditation_council" in doc
        assert "https://www.openstreetmap.org" in doc["map_url"]
        
        code = doc["specialization_code"]
        spec_counts[code] = spec_counts.get(code, 0) + 1

    # Verify each of the 5 specializations has accredited practitioners
    for required_spec in ["general_physician", "dermatologist", "dietitian", "gastroenterologist", "endocrinologist"]:
        assert spec_counts.get(required_spec, 0) >= 1

def test_haversine_distance_calculation():
    """Verify geographical distance formula with known benchmark coordinates."""
    # Distance between Jubilee Hills and Banjara Hills in Hyderabad is approx 4.5 km
    jubilee_lat, jubilee_lon = 17.4325, 78.4071
    banjara_lat, banjara_lon = 17.4156, 78.4487
    dist = calculate_haversine_distance(jubilee_lat, jubilee_lon, banjara_lat, banjara_lon)
    assert 4.0 <= dist <= 5.5

    # Same location should be 0.0 km
    assert calculate_haversine_distance(jubilee_lat, jubilee_lon, jubilee_lat, jubilee_lon) == 0.0

def test_nearby_doctor_search_by_city():
    """Verify city benchmark geocoding and nearest sorting."""
    req = DoctorSearchRequest(
        city="Hyderabad",
        max_distance_km=25.0,
        language="en"
    )
    res = DoctorFinderService.find_doctors(req)
    assert res.total > 0
    assert "Hyderabad" in res.search_center
    assert res.detected_city == "Hyderabad"
    assert len(res.doctors) > 0

    # Ensure doctors are sorted ascending by distance
    distances = [d.distance_km for d in res.doctors if d.distance_km is not None]
    assert distances == sorted(distances)

    # Verify OpenStreetMap routing directions URL
    first_doc = res.doctors[0]
    assert "https://www.openstreetmap.org/directions?engine=fossgis_osrm_car&route=" in first_doc.directions_url

def test_nearby_doctor_search_by_gps():
    """Verify precise GPS coordinates search and nearest doctor resolution."""
    # Apollo Health City Jubilee Hills coordinates
    jubilee_lat, jubilee_lon = 17.4325, 78.4071
    req = DoctorSearchRequest(
        latitude=jubilee_lat,
        longitude=jubilee_lon,
        max_distance_km=15.0,
        language="en"
    )
    res = DoctorFinderService.find_doctors(req)
    assert res.total > 0
    # First doctor should be located right in Jubilee Hills
    closest = res.doctors[0]
    assert closest.distance_km <= 1.0
    assert "Jubilee Hills" in closest.address

def test_specialization_filtering():
    """Verify filtering across all 5 specializations."""
    for spec_code in ["general_physician", "dermatologist", "dietitian", "gastroenterologist", "endocrinologist"]:
        req = DoctorSearchRequest(
            city="Hyderabad",
            specialization_code=spec_code,
            language="en"
        )
        res = DoctorFinderService.find_doctors(req)
        assert res.total >= 1
        assert res.applied_specialization == spec_code
        for doc in res.doctors:
            assert doc.specialization_code == spec_code

def test_query_free_text_search():
    """Verify keyword searching for clinic name or condition."""
    # Search for AIG (Asian Institute of Gastroenterology)
    req = DoctorSearchRequest(
        city="Hyderabad",
        query="AIG",
        language="en"
    )
    res = DoctorFinderService.find_doctors(req)
    assert res.total >= 1
    found_aig = any("AIG" in doc.clinic_or_hospital or "Asian Institute" in doc.clinic_or_hospital for doc in res.doctors)
    assert found_aig

def test_multilingual_responses():
    """Verify Telugu and Hindi localized responses and notices."""
    te_req = DoctorSearchRequest(city="Hyderabad", language="te")
    te_res = DoctorFinderService.find_doctors(te_req)
    assert te_res.language == "te"
    assert "నేషనల్ మెడికల్ కమిషన్" in te_res.verified_notice

    hi_req = DoctorSearchRequest(city="Hyderabad", language="hi")
    hi_res = DoctorFinderService.find_doctors(hi_req)
    assert hi_res.language == "hi"
    assert "चिकित्सक" in hi_res.verified_notice

def test_api_endpoints_integration():
    """Verify FastAPI router endpoints directly."""
    # Specializations endpoint
    specs = get_specializations(language="en")
    assert len(specs) == 5

    # Nearby POST endpoint
    post_res = search_doctors(DoctorSearchRequest(city="Secunderabad", language="en"))
    assert post_res.total > 0
    assert isinstance(post_res, DoctorSearchResponse)

    # Nearby GET endpoint
    get_res = search_doctors_get(city="Bengaluru", specialization_code="dietitian", max_distance_km=30.0, language="en")
    assert get_res.total >= 1
    assert get_res.doctors[0].specialization_code == "dietitian"

