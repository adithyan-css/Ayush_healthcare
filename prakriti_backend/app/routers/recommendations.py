from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.claude_service import ClaudeService

router = APIRouter()
claude_service = ClaudeService()

@router.post("/generate")
async def generate(data: dict, db: AsyncSession = Depends(get_db)):
    result = await claude_service.generate_recommendation("Vata", data.get("symptoms", []), "Winter", [])
    return result

@router.get("/history")
async def get_history(db: AsyncSession = Depends(get_db)): return []

@router.get("/{id}")
async def get_rec(id: int, db: AsyncSession = Depends(get_db)): return {}

@router.delete("/{id}")
async def delete_rec(id: int, db: AsyncSession = Depends(get_db)): return {"status": "deleted"}

@router.post("/prevention")
async def prevention(db: AsyncSession = Depends(get_db)): return {"plan": "Drink warm water"}\n