from typing import Optional, List, Dict, Any
from pydantic import BaseModel

class DoctorItem(BaseModel):
    id: str
    name: str
    name_regional: Optional[str] = None
    specialization_code: str # general_physician, dermatologist, dietitian, gastroenterologist, endocrinologist
    specialty: str           # Human readable title
    specialty_regional: Optional[str] = None
    qualification: str
    experience_years: int
    clinic_or_hospital: str
    clinic_type: str = "specialty_clinic" # multispecialty_hospital, specialty_clinic, private_practice
    address: str
    city: str
    latitude: float
    longitude: float
    distance_km: Optional[float] = None
    rating: float = 4.8
    consultation_fee_inr: float
    available_days: List[str]
    contact_phone: str
    verified: bool = True
    accreditation_council: str = "National Medical Commission (NMC) / Indian Dietetic Association (IDA)"
    map_url: str
    directions_url: str

class SpecializationCategory(BaseModel):
    code: str
    label: str
    label_regional: Optional[str] = None
    icon: str
    focus_areas: List[str]
    clinical_description: str

class DoctorSearchRequest(BaseModel):
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    city: Optional[str] = "Hyderabad"
    query: Optional[str] = None
    specialization_code: Optional[str] = None # general_physician, dermatologist, dietitian, gastroenterologist, endocrinologist
    max_distance_km: float = 25.0
    language: str = "en"

class DoctorSearchResponse(BaseModel):
    total: int
    search_center: str
    detected_city: str
    applied_specialization: Optional[str] = None
    doctors: List[DoctorItem]
    specializations_catalog: List[SpecializationCategory] = []
    map_provider: str = "OpenStreetMap (FOSSGIS / Nominatim)"
    verified_notice: str = "All practitioners listed are verified with National Medical Commission (NMC), State Medical Councils, or Indian Dietetic Association (IDA) credentials. Contact numbers and addresses reflect verified institutional directories."
    language: str = "en"
