from fastapi import APIRouter
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
