import os

FILES = {
    "app/routers/symptoms.py": '''from fastapi import APIRouter
router = APIRouter()
@router.post("/report")
async def report(data: dict):
    return {"status": "success", "message": "Symptoms logged"}
@router.get("/community")
async def community():
    return [{"symptom": "Dry Cough", "count": 140, "trend": "up"}]
@router.get("/clusters")
async def clusters():
    return {"clusters": [{"region": "HSR Layout", "condition": "Vata allergy", "risk": "Medium"}]}
''',
    "app/routers/wearable.py": '''from fastapi import APIRouter
router = APIRouter()
@router.post("/hrv-sync")
async def hrv_sync(data: dict):
    return {"status": "success", "hrv_mean": 65.5, "anomaly_detected": False}
@router.get("/nadi")
async def nadi():
    return {"type": "Pitta-Vata", "hrv_ms": 70.1, "stress_index": 4.5}
@router.get("/trend")
async def trend():
    return [{"day": "Mon", "hrv": 60}, {"day": "Tue", "hrv": 65}]
@router.get("/anomalies")
async def anomalies():
    return [{"timestamp": "2023-10-01T08:00:00Z", "reason": "Sudden drop in HRV indicating fatigue."}]
''',
    "app/routers/vaidya.py": '''from fastapi import APIRouter
router = APIRouter()
@router.get("/patients")
async def patients():
    return [{"patient_id": "P123", "name": "Rahul", "current_dosha": "Kapha"}]
@router.get("/patients/{uid}")
async def patient(uid: str):
    return {"uid": uid, "name": "Rahul", "history_len": 4}
@router.post("/suggest")
async def suggest(data: dict):
    return {"ai_suggestions": ["Prescribe Triphala", "Advise dietary changes"]}
@router.post("/interactions")
async def interactions(data: dict):
    return {"safe": True, "warnings": []}
@router.post("/consult")
async def consult(data: dict):
    return {"consult_id": "C-999", "status": "scheduled"}
@router.patch("/outcome/{consult_id}")
async def outcome(consult_id: str):
    return {"status": "completed"}
''',
    "app/services/ml_service.py": '''class MLService:
    async def generate_forecast(self):
        return {"prediction": "High Pitta issues coming", "accuracy": 0.94}
''',
    "app/services/nlp_service.py": '''class NLPService:
    async def cluster_symptoms(self):
        return {"clusters": ["cluster_A", "cluster_B"]}
''',
    "app/services/pdf_service.py": '''class PDFService:
    async def generate_bulletin(self, data: dict):
        return "https://mock.url/download.pdf"
''',
    "app/services/prakriti_service.py": '''class PrakritiService:
    async def calculate_dosha(self, answers: dict):
        return {"vata": 40, "pitta": 20, "kapha": 40, "dominant": "Vata-Kapha"}
''',
    "app/main.py": '''from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, prakriti, recommendations, heatmap, symptoms, forecast, wearable, vaidya
from app.database import init_db

app = FastAPI(title="PrakritiOS API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def on_startup():
    await init_db()

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(prakriti.router, prefix="/api/v1/prakriti", tags=["Prakriti"])
app.include_router(recommendations.router, prefix="/api/v1/recommendations", tags=["Recommendations"])
app.include_router(heatmap.router, prefix="/api/v1/heatmap", tags=["Heatmap"])
app.include_router(symptoms.router, prefix="/api/v1/symptoms", tags=["Symptoms"])
app.include_router(forecast.router, prefix="/api/v1/forecast", tags=["Forecast"])
app.include_router(wearable.router, prefix="/api/v1/wearable", tags=["Wearable"])
app.include_router(vaidya.router, prefix="/api/v1/vaidya", tags=["Vaidya Copilot"])

@app.get("/")
async def root():
    return {"status": "running", "api": "PrakritiOS Backend v1"}
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
