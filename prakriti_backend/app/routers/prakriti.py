from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db

router = APIRouter()

@router.post("/profile")
async def create_profile(db: AsyncSession = Depends(get_db)): return {"status": "created"}

@router.get("/profile")
async def get_profile(db: AsyncSession = Depends(get_db)): return {"profile": {}}

@router.put("/profile")
async def update_profile(db: AsyncSession = Depends(get_db)): return {"status": "updated"}

@router.post("/vision-analyse")
async def vision_analyse(db: AsyncSession = Depends(get_db)): return {"dosha": "Pitta"}

@router.get("/tips")
async def get_tips(db: AsyncSession = Depends(get_db)): return {"tips": ["Tip 1"]}\n