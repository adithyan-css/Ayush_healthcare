from fastapi import APIRouter
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
