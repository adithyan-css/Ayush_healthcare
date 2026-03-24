import os

FILES = {
    "app/schemas/schemas.py": '''from pydantic import BaseModel, ConfigDict
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
''',
    "app/dependencies.py": '''from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models.user import User
import redis.asyncio as redis
from app.config import settings
from jose import jwt, JWTError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/firebase-verify")
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    try:
        is_blacklisted = await redis_client.get(f"blacklist:{token}")
        if is_blacklisted:
            raise HTTPException(status_code=401, detail="Token blacklisted")
            
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        user_id = payload.get("sub")
        if not user_id: 
            raise HTTPException(status_code=401, detail="Invalid token payload")
            
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()
        if not user: 
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid credentials")
''',
    "app/routers/auth.py": '''from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models.user import User
from app.schemas.schemas import UserCreate, UserResponse
from app.dependencies import get_current_user, redis_client, oauth2_scheme
from datetime import datetime, timedelta
from jose import jwt
from app.config import settings
from typing import Dict

router = APIRouter()

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=60)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm="HS256")

@router.post("/firebase-verify")
async def verify(data: Dict, db: AsyncSession = Depends(get_db)):
    # Mock firebase verify logic
    firebase_uid = data.get("firebase_uid", "mock_uid")
    email = data.get("email", "mock@example.com")
    display_name = data.get("display_name", "Mock User")
    
    result = await db.execute(select(User).where(User.firebase_uid == firebase_uid))
    user = result.scalars().first()
    
    if not user:
        user = User(firebase_uid=firebase_uid, email=email, display_name=display_name)
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
    token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}

@router.post("/refresh")
async def refresh(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    token = create_access_token(data={"sub": str(current_user.id)})
    return {"access_token": token, "token_type": "bearer"}

@router.post("/logout")
async def logout(token: str = Depends(oauth2_scheme)):
    await redis_client.setex(f"blacklist:{token}", 3600, "true")
    return {"msg": "Logged out successfully"}

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_me(data: Dict, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if "display_name" in data:
        current_user.display_name = data["display_name"]
    await db.commit()
    await db.refresh(current_user)
    return current_user
''',
    "app/routers/prakriti.py": '''from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models.user import User
from app.models.prakriti import PrakritiProfile
from app.schemas.schemas import PrakritiProfileCreate, PrakritiProfileResponse
from app.dependencies import get_current_user

router = APIRouter()

@router.post("/profile", response_model=PrakritiProfileResponse)
async def create_profile(data: PrakritiProfileCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    profile = PrakritiProfile(**data.model_dump(), user_id=current_user.id)
    db.add(profile)
    await db.commit()
    await db.refresh(profile)
    return profile

@router.get("/profile", response_model=PrakritiProfileResponse)
async def get_profile(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(PrakritiProfile).where(PrakritiProfile.user_id == current_user.id).order_by(PrakritiProfile.completed_at.desc()))
    profile = result.scalars().first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile

@router.put("/profile", response_model=PrakritiProfileResponse)
async def update_profile(data: PrakritiProfileCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(PrakritiProfile).where(PrakritiProfile.user_id == current_user.id))
    profile = result.scalars().first()
    if not profile:
        profile = PrakritiProfile(**data.model_dump(), user_id=current_user.id)
        db.add(profile)
    else:
        for k, v in data.model_dump().items():
            setattr(profile, k, v)
    await db.commit()
    await db.refresh(profile)
    return profile

@router.post("/vision-analyse")
async def vision_analyse(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return {"dosha": "Pitta", "confidence": 0.85}

@router.get("/tips")
async def get_tips(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return {"tips": ["Drink warm water", "Avoid spicy foods", "Practice cooling pranayama"]}
''',
    "app/routers/recommendations.py": '''from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models.user import User
from app.models.prakriti import PrakritiProfile
from app.models.recommendation import RecommendationSession
from app.schemas.schemas import RecommendationRequest, RecommendationSessionResponse
from app.dependencies import get_current_user
from app.services.claude_service import ClaudeService

router = APIRouter()
claude_service = ClaudeService()

@router.post("/generate", response_model=RecommendationSessionResponse)
async def generate(req: RecommendationRequest, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    # 1. Fetch user Prakriti profile
    p_result = await db.execute(select(PrakritiProfile).where(PrakritiProfile.user_id == current_user.id).order_by(PrakritiProfile.completed_at.desc()))
    profile = p_result.scalars().first()
    dosha = profile.dominant_dosha if profile else "Unknown"
    
    # 2. Fetch last 3 sessions for history-aware prompt
    s_result = await db.execute(select(RecommendationSession).where(RecommendationSession.user_id == current_user.id).order_by(RecommendationSession.created_at.desc()).limit(3))
    history = s_result.scalars().all()
    history_data = [{"symptoms": h.symptoms, "response": h.response_json} for h in history]

    # 3. Call Claude Service
    ai_response = await claude_service.generate_recommendation(dosha, req.symptoms, req.season, history_data)
    
    # 4. Save Session
    session = RecommendationSession(
        user_id=current_user.id,
        symptoms=req.symptoms,
        season=req.season,
        free_text=req.free_text,
        response_json=ai_response,
        prevention_plan=ai_response.get("prevention30", "")
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    
    return session

@router.get("/history")
async def get_history(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(RecommendationSession).where(RecommendationSession.user_id == current_user.id).order_by(RecommendationSession.created_at.desc()))
    return result.scalars().all()

@router.get("/{id}", response_model=RecommendationSessionResponse)
async def get_rec(id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(RecommendationSession).where(RecommendationSession.id == id, RecommendationSession.user_id == current_user.id))
    session = result.scalars().first()
    if not session: raise HTTPException(status_code=404)
    return session

@router.delete("/{id}")
async def delete_rec(id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(RecommendationSession).where(RecommendationSession.id == id, RecommendationSession.user_id == current_user.id))
    session = result.scalars().first()
    if not session: raise HTTPException(status_code=404)
    await db.delete(session)
    await db.commit()
    return {"status": "deleted"}

@router.post("/prevention")
async def prevention(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return {"plan": "Drink warm water and consume ghee to balance Vata during winter."}
''',
    "app/routers/heatmap.py": '''from fastapi import APIRouter
router = APIRouter()
@router.get("/districts")
async def get_districts():
    return [{"district_id": "D1", "state": "KA", "risk_level": "High", "dominant_condition": "Pitta Aggravation"}]
@router.get("/state/{state_id}")
async def get_state(state_id: str):
    return {"state_id": state_id, "active_risks": 15, "trend": "rising"}
@router.get("/trend/{state_id}")
async def get_trend(state_id: str):
    return [{"month": "Jan", "cases": 120}, {"month": "Feb", "cases": 150}]
@router.get("/rising")
async def get_rising():
    return [{"district": "Bangalore Urban", "alert": "Spike in respiratory conditions"}]
@router.post("/refresh")
async def refresh():
    return {"status": "refreshed"}
''',
    "app/routers/forecast.py": '''from fastapi import APIRouter
router = APIRouter()
@router.get("/national")
async def national():
    return {"30_day_trend": "Increasing Vata-related joint issues", "regions": ["North", "South"]}
@router.get("/regions")
async def regions():
    return [{"region": "North", "trend_score": 0.8}]
@router.get("/population")
async def population():
    return {"at_risk": 500000}
@router.get("/seasonal")
async def seasonal():
    return {"current_season": "Hemanta", "advisory": "Consume rich, warm, oily foods."}
@router.get("/explain/{district_id}")
async def explain(district_id: str):
    return {"explanation": "High humidity and dropping temperatures correlate strongly with upcoming Kapha spikes in the region."}
@router.post("/bulletin")
async def bulletin():
    return {"pdf_url": "https://prakritios.mock/bulletin.pdf"}
@router.post("/refresh")
async def refresh(): return {"status": "refreshed"}
''',
    "app/services/claude_service.py": '''from app.config import settings
import json

class ClaudeService:
    async def generate_recommendation(self, dosha: str, symptoms: dict, season: str, history: list):
        # In a real app we construct a huge history-aware prompt here and call Anthropic API.
        # Since I'm mocking for demo-readiness as asked:
        prompt = f"Dosha: {dosha}, Symptoms: {symptoms}, Season: {season}. History: {history}"
        
        response = {
            "herbs": ["Ashwagandha", "Brahmi"],
            "diet": {
                "eat": ["Warm cooked grains", "Ghee"],
                "avoid": ["Cold salads", "Dry crackers"]
            },
            "yoga": ["Surya Namaskar", "Vajrasana"],
            "dinacharya": ["Abhyanga (Oil Massage) before bath", "Early to bed by 10 PM"],
            "prevention30": f"Given your {dosha} dosha and {season} season, risk of joint pain is high. Stay hydrated with warm water."
        }
        return response
'''
}

def main():
    root = "c:/Users/adith/OneDrive/Desktop/ayush_health/prakriti_backend"
    for path, content in FILES.items():
        full_path = os.path.join(root, path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content.strip() + "\\n")
    print("Files updated.")

if __name__ == "__main__":
    main()
