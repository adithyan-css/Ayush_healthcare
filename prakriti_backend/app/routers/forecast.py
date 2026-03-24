from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.ml_service import MLService

router = APIRouter()
ml_service = MLService()

@router.get("/national")
async def national(db: AsyncSession = Depends(get_db)): return await ml_service.generate_forecast()

@router.get("/regions")
async def regions(db: AsyncSession = Depends(get_db)): return []

@router.get("/population")
async def population(db: AsyncSession = Depends(get_db)): return {}

@router.get("/seasonal")
async def seasonal(db: AsyncSession = Depends(get_db)): return {}

@router.get("/explain/{district_id}")
async def explain(district_id: str, db: AsyncSession = Depends(get_db)): return {"explanation": "seasonal factors"}

@router.post("/bulletin")
async def bulletin(db: AsyncSession = Depends(get_db)): return {"pdf": "url"}

@router.post("/refresh")
async def refresh(db: AsyncSession = Depends(get_db)): return {"status": "refreshed"}\n