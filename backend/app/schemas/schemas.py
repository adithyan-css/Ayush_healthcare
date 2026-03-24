from pydantic import BaseModel
from typing import List, Optional, Dict

class UserSchema(BaseModel):
    uid: str
    email: str
    name: str

class PrakritiProfileSchema(BaseModel):
    vata_score: float
    pitta_score: float
    kapha_score: float
    dominant_dosha: str

class RecommendationOutput(BaseModel):
    herbs: List[str]
    diet: Dict[str, List[str]]
    yoga: List[str]
    dinacharya: List[str]
    prevention30: str
