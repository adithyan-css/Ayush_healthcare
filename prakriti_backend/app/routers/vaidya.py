from fastapi import APIRouter, Depends
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
async def outcome(consult_id: str, db: AsyncSession = Depends(get_db)): return {"status": "updated"}\n