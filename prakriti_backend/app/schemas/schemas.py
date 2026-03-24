from datetime import datetime
import uuid
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict


class UserBase(BaseModel):
    firebase_uid: str
    email: str
    display_name: str
    role: str = 'patient'
    language: str = 'en'


class UserCreate(UserBase):
    pass


class UserResponse(UserBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime]
    model_config = ConfigDict(from_attributes=True)


class AuthRegisterRequest(BaseModel):
    email: str
    password: str
    display_name: str
    language: str = 'en'


class AuthLoginRequest(BaseModel):
    email: str
    password: str


class AuthTokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = 'bearer'


class PrakritiProfileBase(BaseModel):
    vata_score: float
    pitta_score: float
    kapha_score: float
    dominant_dosha: str
    risk_score: float


class PrakritiProfileCreate(PrakritiProfileBase):
    pass


class PrakritiProfileResponse(PrakritiProfileBase):
    id: uuid.UUID
    user_id: uuid.UUID
    completed_at: datetime
    model_config = ConfigDict(from_attributes=True)


class RecommendationRequest(BaseModel):
    symptoms: List[str]
    free_text: Optional[str] = None
    variation: Optional[bool] = False


class RecommendationResponseFormat(BaseModel):
    herbs: List[Dict[str, Any]]
    diet: Dict[str, List[Any]]
    yoga: List[Any]
    dinacharya: List[Any]
    prevention_30day: str


class RecommendationSessionResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    symptoms: List[str]
    season: str
    response_json: Dict[str, Any]
    prevention_plan: Optional[str] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class DistrictRiskResponse(BaseModel):
    id: uuid.UUID
    state_code: str
    state_name: str
    risk_score: float
    risk_level: str
    top_condition: str
    trend: str
    monthly_cases: Any
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
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class VaidyaSuggestionResponse(BaseModel):
    formulations: List[str]
    rationale: str
    cautions: List[str]
