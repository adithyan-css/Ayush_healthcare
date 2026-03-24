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
from app.services.weather_service import WeatherService

router = APIRouter()
claude = ClaudeService()
ws = WeatherService()


@router.post('/generate', response_model=RecommendationSessionResponse)
async def generate(req: RecommendationRequest, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
	p_result = await db.execute(select(PrakritiProfile).where(PrakritiProfile.user_id == current_user.id).order_by(PrakritiProfile.completed_at.desc()))
	profile = p_result.scalars().first()
	dosha = profile.dominant_dosha if profile else 'vata'
	vata = profile.vata_score * 10 if profile else 33
	pitta = profile.pitta_score * 10 if profile else 33
	kapha = profile.kapha_score * 10 if profile else 34
	s_result = await db.execute(select(RecommendationSession).where(RecommendationSession.user_id == current_user.id).order_by(RecommendationSession.created_at.desc()).limit(3))
	history = s_result.scalars().all()
	history_data = [{'date': str(h.created_at.date()), 'symptoms': h.symptoms if isinstance(h.symptoms, list) else h.symptoms.get('items', [])} for h in history]
	season = ws.get_current_season()
	ai_response = await claude.generate_recommendation(dosha, vata, pitta, kapha, season, req.symptoms, history_data, req.free_text, current_user.language)
	session = RecommendationSession(
		user_id=current_user.id,
		symptoms=req.symptoms,
		season=season,
		free_text=req.free_text,
		response_json=ai_response,
		prevention_plan=ai_response.get('prevention_30day', '')
	)
	db.add(session)
	await db.commit()
	await db.refresh(session)
	return session


@router.get('/history')
async def get_history(page: int = 1, limit: int = 10, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
	offset = (page - 1) * limit
	result = await db.execute(select(RecommendationSession).where(RecommendationSession.user_id == current_user.id).order_by(RecommendationSession.created_at.desc()).offset(offset).limit(limit))
	return result.scalars().all()


@router.get('/{id}', response_model=RecommendationSessionResponse)
async def get_rec(id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
	result = await db.execute(select(RecommendationSession).where(RecommendationSession.id == id, RecommendationSession.user_id == current_user.id))
	session = result.scalars().first()
	if not session:
		raise HTTPException(status_code=404)
	return session


@router.delete('/{id}')
async def delete_rec(id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
	result = await db.execute(select(RecommendationSession).where(RecommendationSession.id == id, RecommendationSession.user_id == current_user.id))
	session = result.scalars().first()
	if not session:
		raise HTTPException(status_code=404)
	await db.delete(session)
	await db.commit()
	return {'status': 'deleted'}


@router.post('/prevention')
async def prevention(data: dict, current_user: User = Depends(get_current_user)):
	location = data.get('location', 'India')
	risk_score = data.get('risk_score', 50)
	return {'plan': f'30-day prevention plan for {location}. Risk score {risk_score}/100. Maintain consistent sleep schedule, favor warm seasonal foods, practice pranayama daily.'}
