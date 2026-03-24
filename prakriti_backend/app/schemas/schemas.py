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

class PrakritiProfileResponse(BaseModel):
    id: int
    user_id: str
    vata_score: float
    pitta_score: float
    kapha_score: float
    dominant_dosha: str
    risk_score: float
    completed_at: datetime
    model_config = ConfigDict(from_attributes=True)

class RecommendationResponseFormat(BaseModel):
    herbs: List[str]
    diet: Dict[str, List[str]]
    yoga: List[str]
    dinacharya: List[str]
    prevention30: str\n