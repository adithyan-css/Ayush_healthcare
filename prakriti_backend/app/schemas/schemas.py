from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime


class UserBase(BaseModel):
    firebase_uid: str
    email: str
    display_name: str
    role: str = 'patient'
    language: str = 'en'


class UserCreate(UserBase):
    pass


class UserResponse(UserBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime]
    model_config = ConfigDict(from_attributes=True)


class PrakritiProfileBase(BaseModel):
    vata_score: float
    pitta_score: float
    kapha_score: float
    dominant_dosha: str
    risk_score: float


class PrakritiProfileCreate(PrakritiProfileBase):
    pass


class PrakritiProfileResponse(PrakritiProfileBase):
    id: str
    user_id: str
    completed_at: datetime
    model_config = ConfigDict(from_attributes=True)


class RecommendationRequest(BaseModel):
    symptoms: List[str]
    free_text: Optional[str] = None
    variation: Optional[bool] = False


class RecommendationResponseFormat(BaseModel):
    herbs: List[Dict[str, str]]
    diet: Dict[str, List[Dict[str, str]]]
    yoga: List[Dict[str, str]]
    dinacharya: List[Dict[str, str]]
    prevention_30day: str


class RecommendationSessionResponse(BaseModel):
    id: str
    user_id: str
    symptoms: List[str]
    season: str
    response_json: RecommendationResponseFormat
    prevention_plan: Optional[str] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class DistrictRiskResponse(BaseModel):
    id: str
    state_code: str
    state_name: str
    risk_score: float
    risk_level: str
    top_condition: str
    trend: str
    monthly_cases: Dict[str, Any]
    seasons_map: Dict[str, Any]
    latitude: Optional[float]
    longitude: Optional[float]
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class NadiDiagnosisResponse(BaseModel):
    type: str
    hrv_ms: float
    stress_index: float
    is_anomaly: bool


class ForecastResponse(BaseModel):
    conditions: Dict[str, List[float]]
    region_cards: List[Dict[str, Any]]
    population_risks: Dict[str, int]


class WearableReadingRequest(BaseModel):
    readings: List[Dict[str, Any]]


class SymptomReportRequest(BaseModel):
    symptoms: List[str]
    latitude: Optional[float]
    longitude: Optional[float]


class VaidyaSuggestionResponse(BaseModel):
    formulations: List[str]
    rationale: str
    cautions: List[str]
from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime

class UserBase(BaseModel):
    firebase_uid: str
    email: str
    display_name: str
    role: str = "patient"
    language: str = "en"

class UserCreate(UserBase): pass
class UserResponse(UserBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime]
    model_config = ConfigDict(from_attributes=True)

class PrakritiProfileBase(BaseModel):
    vata_score: float
    pitta_score: float
    kapha_score: float
    dominant_dosha: str
    risk_score: float

class PrakritiProfileCreate(PrakritiProfileBase): pass
class PrakritiProfileResponse(PrakritiProfileBase):
    id: str
    user_id: str
    completed_at: datetime
    model_config = ConfigDict(from_attributes=True)

class RecommendationRequest(BaseModel):
    symptoms: List[str]
    free_text: Optional[str] = None
    variation: Optional[bool] = False

class RecommendationResponseFormat(BaseModel):
    herbs: List[Dict[str, str]]
    diet: Dict[str, List[Dict[str, str]]]
    yoga: List[Dict[str, str]]
    dinacharya: List[Dict[str, str]]
    prevention_30day: str

class RecommendationSessionResponse(BaseModel):
    id: str
    user_id: str
    symptoms: List[str]
    season: str
    response_json: RecommendationResponseFormat
    prevention_plan: Optional[str] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class DistrictRiskResponse(BaseModel):
    id: str
    state_code: str
    state_name: str
    risk_score: float
    risk_level: str
    top_condition: str
    trend: str
    monthly_cases: Dict[str, Any]
    seasons_map: Dict[str, Any]
    latitude: Optional[float]
    longitude: Optional[float]
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class NadiDiagnosisResponse(BaseModel):
    type: str
    hrv_ms: float
    stress_index: float
    is_anomaly: bool

class ForecastResponse(BaseModel):
    conditions: Dict[str, List[float]]
    region_cards: List[Dict[str, Any]]
    population_risks: Dict[str, int]

class WearableReadingRequest(BaseModel):
    readings: List[Dict[str, Any]]

class SymptomReportRequest(BaseModel):
    symptoms: List[str]
    latitude: Optional[float]
    longitude: Optional[float]

class VaidyaSuggestionResponse(BaseModel):
    formulations: List[str]
    rationale: str
    cautions: List[str]
