import os

FILES = {
    "requirements.txt": """fastapi
uvicorn
sqlalchemy[asyncio]
asyncpg
greenlet
pydantic
pydantic-settings
redis
firebase-admin
anthropic
python-jose[cryptography]
passlib[bcrypt]
python-multipart
fpdf2
httpx
alembic
""",
    "Dockerfile": """FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
""",
    "docker-compose.yml": """version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://user:password@db:5432/prakriti
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=prakriti
    ports:
      - "5432:5432"
  redis:
    image: redis:7
    ports:
      - "6379:6379"
""",
    ".env.example": """DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/prakriti
REDIS_URL=redis://localhost:6379/0
JWT_SECRET=supersecretkey
CLAUDE_API_KEY=sk-ant-xxx
FIREBASE_CREDENTIALS_JSON={}
""",
    "app/__init__.py": "",
    "app/main.py": """from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, prakriti, recommendations, heatmap, symptoms, forecast, wearable, vaidya
from app.database import init_db

app = FastAPI(title="PrakritiOS API", version="1.0.0")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.on_event("startup")
async def on_startup():
    await init_db()

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(prakriti.router, prefix="/api/v1/prakriti", tags=["prakriti"])
app.include_router(recommendations.router, prefix="/api/v1/recommendations", tags=["recommendations"])
app.include_router(heatmap.router, prefix="/api/v1/heatmap", tags=["heatmap"])
app.include_router(symptoms.router, prefix="/api/v1/symptoms", tags=["symptoms"])
app.include_router(forecast.router, prefix="/api/v1/forecast", tags=["forecast"])
app.include_router(wearable.router, prefix="/api/v1/wearable", tags=["wearable"])
app.include_router(vaidya.router, prefix="/api/v1/vaidya", tags=["vaidya"])

@app.get("/")
async def root(): return {"status": "ok", "app": "PrakritiOS Backend"}
""",
    "app/config.py": """from pydantic_settings import BaseSettings
class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///./test.db"
    REDIS_URL: str = "redis://localhost:6379/0"
    JWT_SECRET: str = "secret"
    CLAUDE_API_KEY: str = ""
    class Config:
        env_file = ".env"
settings = Settings()
""",
    "app/database.py": """from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
""",
    "app/dependencies.py": """from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models.user import User
import redis.asyncio as redis
from app.config import settings
from jose import jwt, JWTError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/firebase-verify")
redis_client = redis.from_url(settings.REDIS_URL)

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    try:
        is_blacklisted = await redis_client.get(f"blacklist:{token}")
        if is_blacklisted:
            raise HTTPException(status_code=401, detail="Token blacklisted")
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        user_id = payload.get("sub")
        if not user_id: raise HTTPException(status_code=401)
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()
        if not user: raise HTTPException(status_code=401)
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
""",
    "app/models/__init__.py": "",
    "app/models/user.py": """from sqlalchemy import Column, String, DateTime, func
from app.database import Base
import uuid

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    firebase_uid = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    display_name = Column(String)
    role = Column(String, default="patient")
    language = Column(String, default="en")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
""",
    "app/models/prakriti.py": """from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, func
from app.database import Base

class PrakritiProfile(Base):
    __tablename__ = "prakriti_profiles"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    vata_score = Column(Float)
    pitta_score = Column(Float)
    kapha_score = Column(Float)
    dominant_dosha = Column(String)
    risk_score = Column(Float)
    completed_at = Column(DateTime(timezone=True), server_default=func.now())
""",
    "app/models/recommendation.py": """from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, JSON, func
from app.database import Base

class RecommendationSession(Base):
    __tablename__ = "recommendation_sessions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    symptoms = Column(JSON)
    free_text = Column(String)
    season = Column(String)
    response_json = Column(JSON)
    prevention_plan = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
""",
    "app/models/district.py": """from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, func
from app.database import Base

class DistrictRisk(Base):
    __tablename__ = "district_risks"
    id = Column(Integer, primary_key=True, index=True)
    state_code = Column(String, index=True)
    state_name = Column(String)
    risk_score = Column(Float)
    risk_level = Column(String)
    top_condition = Column(String)
    trend = Column(String)
    monthly_cases = Column(JSON)
    seasons_map = Column(JSON)
    latitude = Column(Float)
    longitude = Column(Float)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
""",
    "app/models/hrv.py": """from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, ForeignKey, func
from app.database import Base

class HrvReading(Base):
    __tablename__ = "hrv_readings"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    hrv_ms = Column(Float)
    nadi_type = Column(String)
    is_anomaly = Column(Boolean, default=False)
    measured_at = Column(DateTime(timezone=True), server_default=func.now())
""",
    "app/schemas/__init__.py": "",
    "app/schemas/schemas.py": """from pydantic import BaseModel, ConfigDict
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
    prevention30: str
""",
    "app/routers/__init__.py": "",
    "app/routers/auth.py": """from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.user import User
from app.schemas.schemas import UserCreate, UserResponse
from typing import Dict

router = APIRouter()

@router.post("/firebase-verify")
async def verify(data: Dict, db: AsyncSession = Depends(get_db)): return {"token": "mock_jwt_token"}

@router.post("/refresh")
async def refresh(db: AsyncSession = Depends(get_db)): return {"token": "new_mock_jwt_token"}

@router.post("/logout")
async def logout(db: AsyncSession = Depends(get_db)): return {"msg": "Logged out"}

@router.get("/me", response_model=UserResponse)
async def get_me(db: AsyncSession = Depends(get_db)): 
    # Return mock current user (in real implementation, depend on get_current_user)
    return {"id": "1", "firebase_uid": "uid123", "email": "test@test.com", "display_name": "Test", "role": "patient", "language": "en", "created_at": "2023-01-01T00:00:00Z"}

@router.put("/me")
async def update_me(db: AsyncSession = Depends(get_db)): return {"msg": "Updated"}
""",
    "app/routers/prakriti.py": """from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db

router = APIRouter()

@router.post("/profile")
async def create_profile(db: AsyncSession = Depends(get_db)): return {"status": "created"}

@router.get("/profile")
async def get_profile(db: AsyncSession = Depends(get_db)): return {"profile": {}}

@router.put("/profile")
async def update_profile(db: AsyncSession = Depends(get_db)): return {"status": "updated"}

@router.post("/vision-analyse")
async def vision_analyse(db: AsyncSession = Depends(get_db)): return {"dosha": "Pitta"}

@router.get("/tips")
async def get_tips(db: AsyncSession = Depends(get_db)): return {"tips": ["Tip 1"]}
""",
    "app/routers/recommendations.py": """from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.claude_service import ClaudeService

router = APIRouter()
claude_service = ClaudeService()

@router.post("/generate")
async def generate(data: dict, db: AsyncSession = Depends(get_db)):
    result = await claude_service.generate_recommendation("Vata", data.get("symptoms", []), "Winter", [])
    return result

@router.get("/history")
async def get_history(db: AsyncSession = Depends(get_db)): return []

@router.get("/{id}")
async def get_rec(id: int, db: AsyncSession = Depends(get_db)): return {}

@router.delete("/{id}")
async def delete_rec(id: int, db: AsyncSession = Depends(get_db)): return {"status": "deleted"}

@router.post("/prevention")
async def prevention(db: AsyncSession = Depends(get_db)): return {"plan": "Drink warm water"}
""",
    "app/routers/heatmap.py": """from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db

router = APIRouter()

@router.get("/districts")
async def get_districts(db: AsyncSession = Depends(get_db)): return []

@router.get("/state/{state_id}")
async def get_state(state_id: str, db: AsyncSession = Depends(get_db)): return {}

@router.get("/trend/{state_id}")
async def get_trend(state_id: str, db: AsyncSession = Depends(get_db)): return []

@router.get("/rising")
async def get_rising(db: AsyncSession = Depends(get_db)): return []

@router.post("/refresh")
async def refresh(db: AsyncSession = Depends(get_db)): return {"status": "refreshed"}
""",
    "app/routers/symptoms.py": """from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.nlp_service import NLPService

router = APIRouter()
nlp_service = NLPService()

@router.post("/report")
async def report(db: AsyncSession = Depends(get_db)): return {"status": "reported"}

@router.get("/community")
async def community(db: AsyncSession = Depends(get_db)): return []

@router.get("/clusters")
async def clusters(db: AsyncSession = Depends(get_db)): 
    return await nlp_service.cluster_symptoms()
""",
    "app/routers/forecast.py": """from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.ml_service import MLService

router = APIRouter()
ml_service = MLService()

@router.get("/national")
async def national(db: AsyncSession = Depends(get_db)): return await ml_service.generate_forecast()

@router.get("/regions")
async def regions(db: AsyncSession = Depends(get_db)): return []

@router.get("/population")
async def population(db: AsyncSession = Depends(get_db)): return {}

@router.get("/seasonal")
async def seasonal(db: AsyncSession = Depends(get_db)): return {}

@router.get("/explain/{district_id}")
async def explain(district_id: str, db: AsyncSession = Depends(get_db)): return {"explanation": "seasonal factors"}

@router.post("/bulletin")
async def bulletin(db: AsyncSession = Depends(get_db)): return {"pdf": "url"}

@router.post("/refresh")
async def refresh(db: AsyncSession = Depends(get_db)): return {"status": "refreshed"}
""",
    "app/routers/wearable.py": """from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db

router = APIRouter()

@router.post("/hrv-sync")
async def hrv_sync(db: AsyncSession = Depends(get_db)): return {"status": "synced"}

@router.get("/nadi")
async def nadi(db: AsyncSession = Depends(get_db)): return {"type": "Vata"}

@router.get("/trend")
async def trend(db: AsyncSession = Depends(get_db)): return []

@router.get("/anomalies")
async def anomalies(db: AsyncSession = Depends(get_db)): return []
""",
    "app/routers/vaidya.py": """from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db

router = APIRouter()

@router.get("/patients")
async def patients(db: AsyncSession = Depends(get_db)): return []

@router.get("/patients/{uid}")
async def patient(uid: str, db: AsyncSession = Depends(get_db)): return {}

@router.post("/suggest")
async def suggest(db: AsyncSession = Depends(get_db)): return {"suggestions": []}

@router.post("/interactions")
async def interactions(db: AsyncSession = Depends(get_db)): return []

@router.post("/consult")
async def consult(db: AsyncSession = Depends(get_db)): return {"id": 1}

@router.patch("/outcome/{consult_id}")
async def outcome(consult_id: str, db: AsyncSession = Depends(get_db)): return {"status": "updated"}
""",
    "app/services/__init__.py": "",
    "app/services/claude_service.py": """from app.config import settings
import json

class ClaudeService:
    async def generate_recommendation(self, dosha: str, symptoms: list, season: str, history: list):
        # AI prompt logic with Inject last 3 sessions + dosha + symptoms + season
        # Expected Strict JSON
        response = {
            "herbs": ["Ashwagandha"],
            "diet": {"eat": ["Warm foods"], "avoid": ["Cold foods"]},
            "yoga": ["Surya Namaskar"],
            "dinacharya": ["Wake up early"],
            "prevention30": "Increase hydration to avoid Vata imbalance."
        }
        return response
""",
    "app/services/ml_service.py": """class MLService:
    async def generate_forecast(self):
        # Mock Prophet + LSTM
        return {"30_day_prediction": "Rising Pitta disorders due to summer."}
""",
    "app/services/nlp_service.py": """class NLPService:
    async def cluster_symptoms(self):
        return {"clusters": [{"symptom": "fever", "count": 120}]}
""",
    "app/services/weather_service.py": """class WeatherService:
    async def get_current_season(self, lat: float, lon: float):
        return {"season": "Grishma (Summer)", "temp": 35}
""",
    "app/services/pdf_service.py": """class PDFService:
    async def generate_bulletin(self, data: dict):
        return "mock_pdf_link.pdf"
""",
    "app/services/prakriti_service.py": """class PrakritiService:
    async def calculate_dosha(self, answers: dict):
        return {"dominant_dosha": "Vata"}
"""
}

def main():
    root = "c:/Users/adith/OneDrive/Desktop/ayush_health/prakriti_backend"
    for path, content in FILES.items():
        full_path = os.path.join(root, path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w") as f:
            f.write(content.strip() + "\\n")
    print("prakriti_backend generated successfully.")

if __name__ == "__main__":
    main()
