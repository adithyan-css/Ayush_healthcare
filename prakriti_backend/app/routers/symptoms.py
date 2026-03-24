from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.nlp_service import NLPService

router = APIRouter()
nlp_service = NLPService()

@router.post("/report")
async def report(db: AsyncSession = Depends(get_db)): return {"status": "reported"}

@router.get("/community")
async def community(db: AsyncSession = Depends(get_db)): return []

@router.get("/clusters")
async def clusters(db: AsyncSession = Depends(get_db)): 
    return await nlp_service.cluster_symptoms()\n