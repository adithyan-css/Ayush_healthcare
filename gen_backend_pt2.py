import os

FILES = {
    "app/routers/heatmap.py": """from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.schemas.schemas import DistrictRiskResponse
from app.models.district import DistrictRisk
from app.services.weather_service import WeatherService
from app.services.ml_service import MLService
import random

router = APIRouter()
ws = WeatherService()
ml = MLService()

@router.on_event("startup")
async def seed_districts():
    async for db in get_db():
        count = await db.scalar(select(sa.func.count()).select_from(DistrictRisk))
        if count == 0:
            states = ["MH", "KA", "TN", "DL", "UP", "WB", "GJ", "RJ", "KL", "AP"]
            for s in states:
                dr = DistrictRisk(state_code=s, state_name=f"State {s}", risk_score=random.uniform(20, 80), risk_level="Medium", top_condition="Fever", trend="stable", monthly_cases={"Jan":10, "Feb": 20}, seasons_map={"winter":"High"}, latitude=12.9, longitude=77.5)
                db.add(dr)
            await db.commit()
        break

@router.get("/districts", response_model=list[DistrictRiskResponse])
async def get_districts(condition: str = None, season: str = None, db: AsyncSession = Depends(get_db)):
    stmt = select(DistrictRisk)
    if condition: stmt = stmt.where(DistrictRisk.top_condition == condition)
    res = await db.execute(stmt)
    return res.scalars().all()

@router.get("/state/{state_id}", response_model=DistrictRiskResponse)
async def get_state(state_id: str, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(DistrictRisk).where(DistrictRisk.state_code == state_id))
    state = res.scalars().first()
    if not state: raise HTTPException(status_code=404)
    return state

@router.get("/trend/{state_id}")
async def get_trend(state_id: str, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(DistrictRisk).where(DistrictRisk.state_code == state_id))
    state = res.scalars().first()
    if not state: raise HTTPException(status_code=404)
    return {"months": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"], "cases": [10, 20, 15, 30, 25, 40]}

@router.get("/rising", response_model=list[DistrictRiskResponse])
async def get_rising(limit: int = 5, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(DistrictRisk).where(DistrictRisk.trend == 'rising').limit(limit))
    return res.scalars().all()

@router.post("/refresh")
async def refresh(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(DistrictRisk))
    districts = res.scalars().all()
    count = 0
    for d in districts: # mock update
        w = await ws.get_district_weather(d.latitude or 12.0, d.longitude or 77.0)
        s = ws.get_current_season()
        risks = ws.calculate_climate_risk(w, s)
        d.risk_score = min(max(sum(risks.values()) / 4, 10), 100)
        count += 1
    await db.commit()
    return {"updated": count}
""",
    "app/routers/forecast.py": """from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models.district import DistrictRisk
from app.schemas.schemas import ForecastResponse
from app.services.ml_service import MLService
from app.services.weather_service import WeatherService
from app.services.nlp_service import NLPService
from app.services.claude_service import ClaudeService
from app.services.pdf_service import PDFService

router = APIRouter()
ml = MLService()
ws = WeatherService()
nlp = NLPService()
claude = ClaudeService()
pdf = PDFService()

@router.get("/national", response_model=ForecastResponse)
async def national():
    return ml.generate_forecast()

@router.get("/regions")
async def regions():
    return ml.generate_forecast()["region_cards"]

@router.get("/population")
async def population():
    return ml.generate_forecast()["population_risks"]

@router.get("/seasonal")
async def seasonal():
    season = ws.get_current_season()
    advisories = {
        "winter": "Consume rich, warm, oily foods. Protect against dry Vata and Kapha congestion.",
        "summer": "Stay hydrated, favor cooling foods like cucumber and buttermilk. Minimize Pitta excess.",
        "monsoon": "Drink boiled water, avoid raw foods to prevent Agni sluggishness.",
        "autumn": "Balance Pitta spike with moderate, grounding foods."
    }
    return {"season": season, "advisory": advisories.get(season, "")}

@router.get("/explain/{district_id}")
async def explain(district_id: str, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(DistrictRisk).where(DistrictRisk.id == district_id))
    d = res.scalars().first()
    if not d: return {"reasons": ["District not found. Default reason."]}
    w = await ws.get_district_weather(d.latitude, d.longitude)
    s = nlp.get_signal_summary(d.state_code)
    weather_summary = f"Temp {w.temperature}C, Humidity {w.humidity}%"
    reasons = await claude.generate_xai_explanation(d.state_name, d.risk_level, d.risk_score, d.top_condition, d.trend, weather_summary, s.summary)
    return {"reasons": reasons}

@router.post("/bulletin")
async def bulletin(district_id: str, db: AsyncSession = Depends(get_db)):
    d = await db.scalar(select(DistrictRisk).where(DistrictRisk.id == district_id))
    if not d: return {"pdf_base64": "", "district": "Unknown"}
    w = await ws.get_district_weather(d.latitude, d.longitude)
    s = nlp.get_signal_summary(d.state_code)
    w_sum = f"Temp {w.temperature}C"
    xai = await claude.generate_xai_explanation(d.state_name, d.risk_level, d.risk_score, d.top_condition, d.trend, w_sum, s.summary)
    seas = (await seasonal())["advisory"]
    b64 = pdf.generate_bulletin(d.state_name, d.risk_level, d.risk_score, [d.top_condition], xai, seas)
    return {"pdf_base64": b64, "district": d.state_name}
""",
    "app/routers/wearable.py": """from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models.user import User
from app.models.hrv import HrvReading
from app.schemas.schemas import WearableReadingRequest, NadiDiagnosisResponse
from app.dependencies import get_current_user
from app.services.ml_service import MLService
from datetime import datetime, timedelta

router = APIRouter()
ml = MLService()

@router.post("/hrv-sync")
async def hrv_sync(req: WearableReadingRequest, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    readings = []
    saved = 0
    for r in req.readings:
        ms = float(r["hrv_ms"])
        nadi = ml.detect_nadi_type(ms)
        hist = await db.scalars(select(HrvReading.hrv_ms).where(HrvReading.user_id == current_user.id).order_by(HrvReading.measured_at.desc()).limit(10))
        h_arr = list(hist.all())
        h_arr.append(ms)
        anom = ml.detect_anomaly(h_arr)
        
        rd = HrvReading(user_id=current_user.id, hrv_ms=ms, nadi_type=nadi, is_anomaly=anom)
        db.add(rd)
        saved += 1
    await db.commit()
    return {"saved": saved, "anomaly_detected": anom if 'anom' in locals() else False}

@router.get("/nadi", response_model=NadiDiagnosisResponse)
async def nadi(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    hist = await db.scalars(select(HrvReading).where(HrvReading.user_id == current_user.id).order_by(HrvReading.measured_at.desc()).limit(30))
    h_arr = list(hist.all())
    if not h_arr: return {"type": "Unknown", "hrv_ms": 0, "stress_index": 0, "is_anomaly": False}
    avg = sum(x.hrv_ms for x in h_arr) / len(h_arr)
    t = ml.detect_nadi_type(avg)
    anom = any(x.is_anomaly for x in h_arr)
    return {"type": t, "hrv_ms": avg, "stress_index": 500/avg if avg>0 else 100, "is_anomaly": anom}

@router.get("/trend")
async def trend(days: int = 30, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    hist = await db.scalars(select(HrvReading).where(HrvReading.user_id == current_user.id).order_by(HrvReading.measured_at.asc()).limit(30))
    return [{"date": h.measured_at, "hrv_ms": h.hrv_ms, "nadi_type": h.nadi_type} for h in hist.all()]

@router.get("/anomalies")
async def anomalies(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    hist = await db.scalars(select(HrvReading).where(HrvReading.user_id == current_user.id, HrvReading.is_anomaly == True).order_by(HrvReading.measured_at.desc()))
    return [{"date": h.measured_at, "hrv_ms": h.hrv_ms, "nadi_type": h.nadi_type} for h in hist.all()]
""",
    "app/routers/vaidya.py": """from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models.user import User
from app.models.prakriti import PrakritiProfile
from app.models.recommendation import RecommendationSession
from app.schemas.schemas import VaidyaSuggestionResponse
from app.dependencies import get_current_user
from app.services.claude_service import ClaudeService

router = APIRouter()
claude = ClaudeService()

@router.get("/patients")
async def patients(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db), search: str = ""):
    if current_user.role != "doctor": raise HTTPException(status_code=403, detail="Doctor access only")
    stmt = select(User).where(User.role == 'patient')
    if search: stmt = stmt.where(User.display_name.ilike(f"%{search}%"))
    users = await db.scalars(stmt)
    return users.all()

@router.get("/patients/{uid}")
async def patient(uid: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if current_user.role != "doctor": raise HTTPException(status_code=403)
    u = await db.scalar(select(User).where(User.id == uid))
    p = await db.scalar(select(PrakritiProfile).where(PrakritiProfile.user_id == uid).order_by(PrakritiProfile.completed_at.desc()))
    s = await db.scalars(select(RecommendationSession).where(RecommendationSession.user_id == uid).order_by(RecommendationSession.created_at.desc()).limit(5))
    return {"user": u, "profile": p, "sessions": s.all()}

@router.post("/suggest", response_model=VaidyaSuggestionResponse)
async def suggest(data: dict, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    symptoms = data.get("symptoms", [])
    dosha = data.get("dosha", "Vata")
    uid = data.get("patient_uid", "")
    hist_raw = []
    if uid:
        s = await db.scalars(select(RecommendationSession).where(RecommendationSession.user_id == uid).order_by(RecommendationSession.created_at.desc()).limit(3))
        hist_raw = [{"symptoms": h.symptoms, "response": h.response_json} for h in s]
    return await claude.generate_vaidya_suggestion(symptoms, dosha, hist_raw)

@router.post("/interactions")
async def interactions(data: dict):
    return {"safe": True, "warnings": [], "note": "Herb-drug interaction check requires CCRAS database integration — mock response for demo"}

@router.post("/consult")
async def consult(data: dict, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if current_user.role != "doctor": raise HTTPException(status_code=403)
    # mock saving a consult session mapping
    return {"status": "saved", "consult_id": "c_mock"}

@router.patch("/outcome/{consult_id}")
async def outcome(consult_id: str, data: dict, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if current_user.role != "doctor": raise HTTPException(status_code=403)
    return {"status": "updated", "consult_id": consult_id}
""",
    "app/routers/symptoms.py": """from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models.user import User
from app.models.symptom import SymptomReport
from app.schemas.schemas import SymptomReportRequest
from app.dependencies import get_current_user

router = APIRouter()

@router.post("/report")
async def report(req: SymptomReportRequest, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    sr = SymptomReport(user_id=current_user.id, symptoms={"items": req.symptoms}, latitude=req.latitude, longitude=req.longitude)
    db.add(sr)
    await db.commit()
    return {"status": "success", "message": "Symptoms logged"}

@router.get("/community")
async def community(db: AsyncSession = Depends(get_db)):
    s = await db.scalars(select(SymptomReport).order_by(SymptomReport.created_at.desc()).limit(100))
    cDict = {}
    for r in s:
        for item in r.symptoms.get("items", []):
            cDict[item] = cDict.get(item, 0) + 1
    top = sorted(cDict.items(), key=lambda x: -x[1])[:10]
    return [{"symptom": k, "count": v, "trend": "up"} for k,v in top]

@router.get("/clusters")
async def clusters(db: AsyncSession = Depends(get_db)):
    return {"clusters": [{"region": "Indiranagar", "condition": "Vata allergy", "risk": "Medium"}]}
"""
}

def main():
    root = "c:/Users/adith/OneDrive/Desktop/ayush_health/prakriti_backend"
    for path, content in FILES.items():
        fp = os.path.join(root, path)
        os.makedirs(os.path.dirname(fp), exist_ok=True)
        with open(fp, "w", encoding="utf-8") as f:
            f.write(content.strip() + "\\n")
    print("Backend part 2 scaffold completed.")

if __name__ == "__main__":
    main()
