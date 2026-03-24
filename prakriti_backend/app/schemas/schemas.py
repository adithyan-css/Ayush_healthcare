from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime

class UserBase(BaseModel):
    firebase_uid: str
    email: str
    display_name: str
    role: str = "patient"
    language: str = "en"

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

class PrakritiProfileCreate(PrakritiProfileBase): pass

class PrakritiProfileResponse(PrakritiProfileBase):
    id: str
    user_id: str
    completed_at: datetime
    model_config = ConfigDict(from_attributes=True)

class RecommendationRequest(BaseModel):
    symptoms: Dict[str, Any]
    season: str
    free_text: Optional[str] = None

class RecommendationResponseFormat(BaseModel):
    herbs: List[str]
    diet: Dict[str, List[str]]
    yoga: List[str]
    dinacharya: List[str]
    prevention30: str

class RecommendationSessionResponse(BaseModel):
    id: str
    user_id: str
    symptoms: Dict[str, Any]
    season: str
    response_json: RecommendationResponseFormat
    prevention_plan: Optional[str] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
