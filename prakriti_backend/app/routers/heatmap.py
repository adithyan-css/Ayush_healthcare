from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db

router = APIRouter()

@router.get("/districts")
async def get_districts(db: AsyncSession = Depends(get_db)): return []

@router.get("/state/{state_id}")
async def get_state(state_id: str, db: AsyncSession = Depends(get_db)): return {}

@router.get("/trend/{state_id}")
async def get_trend(state_id: str, db: AsyncSession = Depends(get_db)): return []

@router.get("/rising")
async def get_rising(db: AsyncSession = Depends(get_db)): return []

@router.post("/refresh")
async def refresh(db: AsyncSession = Depends(get_db)): return {"status": "refreshed"}\n