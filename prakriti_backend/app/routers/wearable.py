from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db

router = APIRouter()

@router.post("/hrv-sync")
async def hrv_sync(db: AsyncSession = Depends(get_db)): return {"status": "synced"}

@router.get("/nadi")
async def nadi(db: AsyncSession = Depends(get_db)): return {"type": "Vata"}

@router.get("/trend")
async def trend(db: AsyncSession = Depends(get_db)): return []

@router.get("/anomalies")
async def anomalies(db: AsyncSession = Depends(get_db)): return []\n