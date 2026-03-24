from fastapi import APIRouter
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
