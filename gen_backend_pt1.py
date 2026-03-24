import os

FILES = {
    "alembic.ini": """[alembic]
script_location = alembic
sqlalchemy.url = postgresql+asyncpg://user:password@localhost:5432/prakriti
[post_write_hooks]
[loggers]
keys = root,sqlalchemy,alembic
[handlers]
keys = console
[formatters]
keys = generic
[logger_root]
level = WARN
handlers = console
qualname =
[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine
[logger_alembic]
level = INFO
handlers =
qualname = alembic
[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic
[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
""",
    "alembic/env.py": """import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context
from app.database import Base
from app.config import settings
import app.models.user
import app.models.prakriti
import app.models.recommendation
import app.models.district
import app.models.hrv
import app.models.symptom

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    url = settings.DATABASE_URL
    context.configure(
        url=url, target_metadata=target_metadata, literal_binds=True, dialect_opts={"paramstyle": "named"}
    )
    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()

async def run_async_migrations() -> None:
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = settings.DATABASE_URL
    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()

def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
""",
    "alembic/versions/001_initial.py": """\"\"\"initial
Revision ID: 001
Revises: 
Create Date: 2026-03-24 10:00:00.000000
\"\"\"
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    pass

def downgrade() -> None:
    pass
""",
    ".gitignore": """__pycache__/
*.pyc
*.pyo
.env
test.db
*.db
alembic/versions/*.pyc
""",
    ".env.example": """DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/prakriti
REDIS_URL=redis://localhost:6379/0
# Generate with: python -c "import secrets; print(secrets.token_hex(32))"
JWT_SECRET=REPLACE_WITH_32_CHAR_RANDOM_STRING
ANTHROPIC_API_KEY=sk-ant-YOUR_KEY_HERE
OPENWEATHER_API_KEY=YOUR_KEY_HERE
""",
    "requirements.txt": """fastapi
uvicorn[standard]
sqlalchemy[asyncio]
asyncpg
aiosqlite
greenlet
pydantic
pydantic-settings
redis[hiredis]
firebase-admin
anthropic
python-jose[cryptography]
passlib[bcrypt]
python-multipart
fpdf2
httpx
alembic
path-lib
python-dotenv
""",
    "app/models/symptom.py": """import uuid
from datetime import datetime
from sqlalchemy import Float, DateTime, ForeignKey, JSON, func, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING, Dict, Any
from app.database import Base

if TYPE_CHECKING:
    from app.models.user import User

class SymptomReport(Base):
    __tablename__ = "symptom_reports"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    
    symptoms: Mapped[Dict[str, Any]] = mapped_column(JSON)
    latitude: Mapped[float] = mapped_column(Float, nullable=True)
    longitude: Mapped[float] = mapped_column(Float, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship("User", back_populates="symptom_reports")
""",
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
""",
    "app/services/claude_service.py": """import json
from fastapi import HTTPException
from anthropic import AsyncAnthropic
from app.config import settings

class ClaudeService:
    def __init__(self):
        self.api_key = settings.CLAUDE_API_KEY
        self.client = AsyncAnthropic(api_key=self.api_key) if self.api_key else None

    async def generate_recommendation(self, dosha: str, vata: float, pitta: float, kapha: float, season: str, symptoms: list, history: list, free_text: str = None, lang: str = "en"):
        if not self.client:
            return {
                "herbs": [{"name":"Ashwagandha","benefit":"Stress relif","dosage":"1 tsp","timing":"night"}],
                "diet": {"eat": [{"food":"Warm grains","reason":"Balances Vata"}], "avoid": [{"food":"Cold salads","reason":"Increases Vata"}]},
                "yoga": [{"name":"Surya Namaskar","duration":"10 min","benefit":"Warm up"}],
                "dinacharya": [{"time":"06:00","activity":"Wake up"}],
                "prevention_30day": f"API KEY MISSING. Default response applied for {dosha} dosha."
            }

        hist_str = "\\n".join([f"- {h['date']}: {', '.join(h['symptoms'])}" for h in history]) if history else "None"
        prompt = f\"\"\"You are an expert AYUSH health advisor.
User Prakriti: {dosha} dosha ({vata}% Vata, {pitta}% Pitta, {kapha}% Kapha)
Current Season: {season}
Past consultations (last 3):
{hist_str}
Current symptoms: {', '.join(symptoms)}
{free_text or ''}
Return ONLY valid JSON (no markdown fences, no explanation):
{{"herbs":[{{"name":"","benefit":"","dosage":"","timing":""}}],"diet":{{"eat":[{{"food":"","reason":""}}],"avoid":[{{"food":"","reason":""}}]}},"yoga":[{{"name":"","duration":"","benefit":""}}],"dinacharya":[{{"time":"","activity":""}}],"prevention_30day":"string paragraph"}}
Respond in language: {lang}
\"\"\"
        try:
            res = await self.client.messages.create(
                model="claude-3-5-sonnet-20240620", max_tokens=2000, temperature=0.2,
                messages=[{"role": "user", "content": prompt}]
            )
            text = res.content[0].text.strip()
            if text.startswith("```json"): text = text[7:-3].strip()
            elif text.startswith("```"): text = text[3:-3].strip()
            return json.loads(text)
        except Exception as e:
            print(f"Claude Error: {e}")
            raise HTTPException(status_code=500, detail="Failed to fetch AI recommendation.")

    async def generate_xai_explanation(self, district: str, level: str, score: float, condition: str, trend: str, weather_summary: str, social_summary: str):
        if not self.client: return ["High humidity detected.", "Rising social signals."]
        prompt = f\"\"\"You are a public health AI. District: {district}, Risk: {level} ({score}/100), Top condition: {condition}, Trend: {trend}, Weather: {weather_summary}, Social signals: {social_summary}. Return ONLY a JSON array of strings, each a specific data-driven reason. Example format: ["Reason 1 with numbers", "Reason 2"]\"\"\"
        try:
            res = await self.client.messages.create(model="claude-3-5-sonnet-20240620", max_tokens=1000, temperature=0.1, messages=[{"role": "user", "content": prompt}])
            text = res.content[0].text.strip()
            if text.startswith("```json"): text = text[7:-3].strip()
            elif text.startswith("```"): text = text[3:-3].strip()
            return json.loads(text)
        except Exception: return ["Weather indicators suggest risk.", "Social trends confirm anomalies."]

    async def generate_vaidya_suggestion(self, symptoms: list, dosha: str, history: list):
        if not self.client: return {"formulations": ["Triphala"], "rationale": "Balances all doshas", "cautions": ["Do not overdose"]}
        prompt = f"Patient Dosha: {dosha}. Symptoms: {symptoms}. History: {history}. Return ONLY strict JSON: {{\"formulations\": [\"\"], \"rationale\": \"\", \"cautions\": [\"\"]}}"
        try:
            res = await self.client.messages.create(model="claude-3-5-sonnet-20240620", max_tokens=1000, temperature=0.2, messages=[{"role": "user", "content": prompt}])
            text = res.content[0].text.strip()
            if text.startswith("```json"): text = text[7:-3].strip()
            elif text.startswith("```"): text = text[3:-3].strip()
            return json.loads(text)
        except: return {"formulations": ["Consult specialist"], "rationale": "API Error", "cautions": []}
""",
    "app/services/weather_service.py": """import httpx
from datetime import datetime
from app.config import settings

class WeatherData:
    def __init__(self, temp: float, humidity: float, rainfall: float, aqi: int, condition: str):
        self.temperature = temp
        self.humidity = humidity
        self.rainfall = rainfall
        self.aqi = aqi
        self.condition = condition

class WeatherService:
    async def get_district_weather(self, lat: float, lon: float) -> WeatherData:
        key = settings.OPENWEATHER_API_KEY
        if not key or key == "YOUR_KEY_HERE":
            return WeatherData(28, 65, 0, 2, "clear")
        async with httpx.AsyncClient() as client:
            try:
                res = await client.get(f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={key}&units=metric")
                data = res.json()
                temp = data.get("main", {}).get("temp", 28)
                hum = data.get("main", {}).get("humidity", 65)
                cond = data.get("weather", [{}])[0].get("main", "clear")
                return WeatherData(temp, hum, 0, 2, cond)
            except:
                return WeatherData(28, 65, 0, 2, "clear")

    def calculate_climate_risk(self, weather: WeatherData, season: str):
        risks = {"Fever/Viral": 0, "Respiratory": 0, "Joint": 0, "Digestive": 0}
        if weather.humidity > 80 and season == "monsoon": risks["Fever/Viral"] = min(100, weather.humidity * 1.2)
        if weather.aqi >= 3: risks["Respiratory"] += weather.aqi * 20
        if weather.temperature < 15: 
            risks["Joint"] += (15 - weather.temperature) * 4
            risks["Respiratory"] += 25
        if weather.rainfall > 50: risks["Digestive"] += 40
        return risks

    def get_current_season(self):
        m = datetime.now().month
        if m in [12, 1, 2]: return "winter"
        if m in [3, 4, 5]: return "summer"
        if m in [6, 7, 8, 9]: return "monsoon"
        return "autumn"
""",
    "app/services/ml_service.py": """import math
import random

class MLService:
    def generate_forecast(self):
        days = list(range(30))
        conds = {"Respiratory": 30, "Digestive": 20, "Fever/Viral": 40, "Skin": 15, "Joint": 25}
        preds = {}
        for c, base in conds.items():
            preds[c] = [round(base + 10 * math.sin(d/5) + random.uniform(-5, 5), 1) for d in days]
        
        cards = [
            {"region": "Maharashtra", "condition": "Fever/Viral", "peak_in_days": 5, "severity": "high"},
            {"region": "Delhi", "condition": "Respiratory", "peak_in_days": 12, "severity": "critical"},
            {"region": "Karnataka", "condition": "Digestive", "peak_in_days": 2, "severity": "medium"},
            {"region": "Kerala", "condition": "Skin", "peak_in_days": 28, "severity": "low"}
        ]
        pop = {"Children": 65, "Adults": 45, "Elderly": 78, "Urban": 55, "Rural": 60}
        return {"conditions": preds, "region_cards": cards, "population_risks": pop}

    def detect_nadi_type(self, hrv_ms: float):
        if hrv_ms > 50: return "vata_nadi"
        if hrv_ms >= 30: return "pitta_nadi"
        return "kapha_nadi"

    def detect_anomaly(self, readings: list):
        if len(readings) < 5: return False
        mean = sum(readings) / len(readings)
        var = sum((x - mean)**2 for x in readings) / len(readings)
        std = math.sqrt(var)
        return abs(readings[-1] - mean) > 2 * std
""",
    "app/services/pdf_service.py": """import base64
import os
from fpdf import FPDF
class PDFService:
    def generate_bulletin(self, district_name, risk_level, risk_score, top_conditions, xai_reasons, seasonal_advisory):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=16, style='B')
        pdf.cell(200, 10, txt="PrakritiOS Health Bulletin", ln=1, align='C')
        pdf.set_font("Arial", size=14, style='B')
        pdf.cell(200, 10, txt=f"District: {district_name} | Risk: {risk_level} ({risk_score}/100)", ln=1, align='L')
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt=f"Top Conditions: {', '.join(top_conditions)}", ln=1, align='L')
        pdf.ln(5)
        pdf.set_font("Arial", size=12, style='B')
        pdf.cell(200, 10, txt="AI Reasoning:", ln=1)
        pdf.set_font("Arial", size=11)
        for r in xai_reasons:
            pdf.cell(200, 8, txt=f"- {r}", ln=1)
        pdf.ln(5)
        pdf.set_font("Arial", size=12, style='B')
        pdf.cell(200, 10, txt="Seasonal Advisory:", ln=1)
        pdf.set_font("Arial", size=11)
        pdf.multi_cell(0, 10, txt=seasonal_advisory)
        
        path = "/tmp/bulletin.pdf"
        os.makedirs("/tmp", exist_ok=True)
        pdf.output(path)
        with open(path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")
        return b64

    def generate_arogya_report(self, user_name, dosha, history):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=16, style='B')
        pdf.cell(200, 10, txt="Arogya Report", ln=1, align='C')
        path = "/tmp/arogya.pdf"
        os.makedirs("/tmp", exist_ok=True)
        pdf.output(path)
        with open(path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")
        return b64
""",
    "app/services/nlp_service.py": """import random

class SocialSignalSummary:
    def __init__(self, state_code, total, top, summary):
        self.state_code = state_code
        self.total_signals = total
        self.top_symptoms = top
        self.summary = summary

class NLPService:
    def get_signal_summary(self, state_code: str):
        # Replace with real Twitter/X API v2 call using TWITTER_BEARER_TOKEN when available
        total = random.randint(20, 200)
        symptoms = ["fever", "cough", "fatigue", "body ache"]
        random.shuffle(symptoms)
        top = symptoms[:3]
        summary = f"{total} health signals detected, top: {top[0]}"
        return SocialSignalSummary(state_code, total, top, summary)
"""
}

def main():
    root = "c:/Users/adith/OneDrive/Desktop/ayush_health/prakriti_backend"
    for path, content in FILES.items():
        fp = os.path.join(root, path)
        os.makedirs(os.path.dirname(fp), exist_ok=True)
        with open(fp, "w", encoding="utf-8") as f:
            f.write(content.strip() + "\\n")
    print("Backend part 1 scaffold completed.")

if __name__ == "__main__":
    main()
