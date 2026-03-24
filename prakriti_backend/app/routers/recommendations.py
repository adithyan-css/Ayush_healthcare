from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models.user import User
from app.models.prakriti import PrakritiProfile
from app.models.recommendation import RecommendationSession
from app.schemas.schemas import RecommendationRequest, RecommendationSessionResponse
from app.dependencies import get_current_user
from app.services.claude_service import ClaudeService

router = APIRouter()
claude_service = ClaudeService()

@router.post("/generate", response_model=RecommendationSessionResponse)
async def generate(req: RecommendationRequest, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    # 1. Fetch user Prakriti profile
    p_result = await db.execute(select(PrakritiProfile).where(PrakritiProfile.user_id == current_user.id).order_by(PrakritiProfile.completed_at.desc()))
    profile = p_result.scalars().first()
    dosha = profile.dominant_dosha if profile else "Unknown"
    
    # 2. Fetch last 3 sessions for history-aware prompt
    s_result = await db.execute(select(RecommendationSession).where(RecommendationSession.user_id == current_user.id).order_by(RecommendationSession.created_at.desc()).limit(3))
    history = s_result.scalars().all()
    history_data = [{"symptoms": h.symptoms, "response": h.response_json} for h in history]

    # 3. Call Claude Service
    ai_response = await claude_service.generate_recommendation(dosha, req.symptoms, req.season, history_data)
    
    # 4. Save Session
    session = RecommendationSession(
        user_id=current_user.id,
        symptoms=req.symptoms,
        season=req.season,
        free_text=req.free_text,
        response_json=ai_response,
        prevention_plan=ai_response.get("prevention30", "")
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    
    return session

@router.get("/history")
async def get_history(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(RecommendationSession).where(RecommendationSession.user_id == current_user.id).order_by(RecommendationSession.created_at.desc()))
    return result.scalars().all()

@router.get("/{id}", response_model=RecommendationSessionResponse)
async def get_rec(id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(RecommendationSession).where(RecommendationSession.id == id, RecommendationSession.user_id == current_user.id))
    session = result.scalars().first()
    if not session: raise HTTPException(status_code=404)
    return session

@router.delete("/{id}")
async def delete_rec(id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(RecommendationSession).where(RecommendationSession.id == id, RecommendationSession.user_id == current_user.id))
    session = result.scalars().first()
    if not session: raise HTTPException(status_code=404)
    await db.delete(session)
    await db.commit()
    return {"status": "deleted"}

@router.post("/prevention")
async def prevention(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return {"plan": "Drink warm water and consume ghee to balance Vata during winter."}
