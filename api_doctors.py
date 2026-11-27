from typing import List, Optional
from fastapi import APIRouter
from schema_doctor import (
    DoctorSearchRequest, DoctorSearchResponse, SpecializationCategory
)
from doctor_service import DoctorFinderService, find_nearby_doctors

router = APIRouter(prefix="/doctors", tags=["Doctor & Dietitian Finder"])

@router.get(
    "/specializations",
    response_model=List[SpecializationCategory],
    summary="List accredited clinical specializations",
    description="Returns the 5 clinical specializations (General physician, Dermatologist, Dietitian, Gastroenterologist, Endocrinologist) with multilingual descriptions and focus areas."
)
def get_specializations(language: str = "en"):
    return DoctorFinderService.get_specializations(lang=language)

@router.post(
    "/nearby",
    response_model=DoctorSearchResponse,
    summary="Find nearby verified doctors and clinical practitioners",
    description="Locates certified doctors, hospital centers, and clinical dietitians based on GPS coordinates or manual city query, computing exact Haversine distance and OpenStreetMap turn-by-turn routing."
)
def search_doctors(request: DoctorSearchRequest):
    return find_nearby_doctors(request)

@router.get(
    "/nearby",
    response_model=DoctorSearchResponse,
    summary="Query nearby verified doctors via GET query params",
    description="GET alternative for search_doctors supporting direct URL query parameters."
)
def search_doctors_get(
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    city: Optional[str] = "Hyderabad",
    query: Optional[str] = None,
    specialization_code: Optional[str] = None,
    max_distance_km: float = 25.0,
    language: str = "en"
):
    request = DoctorSearchRequest(
        latitude=latitude,
        longitude=longitude,
        city=city,
        query=query,
        specialization_code=specialization_code,
        max_distance_km=max_distance_km,
        language=language
    )
    return find_nearby_doctors(request)
