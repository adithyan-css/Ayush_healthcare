from fastapi import APIRouter
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
