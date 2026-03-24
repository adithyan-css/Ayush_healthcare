from fastapi import APIRouter
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
