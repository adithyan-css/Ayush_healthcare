from fastapi import APIRouter
router = APIRouter()

@router.get("/patients")
async def patients(): pass

@router.get("/patients/{uid}")
async def patient(uid: str): pass

@router.post("/suggest")
async def suggest(): pass

@router.post("/interactions")
async def interactions(): pass

@router.post("/consult")
async def consult(): pass

@router.patch("/outcome/{consult_id}")
async def outcome(consult_id: str): pass
