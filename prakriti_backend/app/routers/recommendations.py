import uuid
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models.user import User
from app.models.prakriti import PrakritiProfile
from app.models.recommendation import RecommendationSession
from app.schemas.schemas import RecommendationRequest
from app.dependencies import get_current_user, success_response, resolve_language
from app.services.recommendation_service import RecommendationService
from app.services.weather_service import WeatherService
from app.services.pdf_service import PDFService

router = APIRouter()
recommendation_service = RecommendationService()
ws = WeatherService()
pdf_service = PDFService()


@router.post('/generate')
async def generate(req: RecommendationRequest, request: Request, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
	try:
		p_result = await db.execute(select(PrakritiProfile).where(PrakritiProfile.user_id == current_user.id).order_by(PrakritiProfile.completed_at.desc()))
		profile = p_result.scalars().first()
		dosha = profile.dominant_dosha if profile else 'vata'
		vata = (profile.vata_score * 10) if profile else 33
		pitta = (profile.pitta_score * 10) if profile else 33
		kapha = (profile.kapha_score * 10) if profile else 34

		s_result = await db.execute(select(RecommendationSession).where(RecommendationSession.user_id == current_user.id).order_by(RecommendationSession.created_at.desc()).limit(3))
		history = s_result.scalars().all()
		history_data = [
			{
				'date': str(h.created_at.date()),
				'symptoms': h.symptoms if isinstance(h.symptoms, list) else h.symptoms.get('items', []),
			}
			for h in history
		]
		if req.history:
			history_data = req.history[:3]

		season = req.season or ws.get_current_season()
		free_text = req.free_text
		if req.variation:
			suffix = ', please vary the suggestions from previous recommendations'
			free_text = (free_text or '') + suffix

		language = req.language or resolve_language(request, current_user.language)
		ai_response = await recommendation_service.generate_recommendation(dosha, vata, pitta, kapha, season, req.symptoms, history_data, free_text, language)
		session = RecommendationSession(
			user_id=current_user.id,
			symptoms=req.symptoms,
			season=season,
			free_text=free_text,
			response_json=ai_response,
			prevention_plan=ai_response.get('prevention_plan', '') or ai_response.get('prevention_30day', ''),
		)
		db.add(session)
		await db.commit()
		await db.refresh(session)
		session.symptoms = req.symptoms
		return success_response(session, 'Recommendation generated')
	except Exception as exc:
		await db.rollback()
		raise HTTPException(status_code=500, detail=f'Unable to generate recommendation: {exc}')


@router.get('/history')
async def get_history(page: int = 1, limit: int = 10, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
	try:
		offset = (page - 1) * limit
		result = await db.execute(select(RecommendationSession).where(RecommendationSession.user_id == current_user.id).order_by(RecommendationSession.created_at.desc()).offset(offset).limit(limit))
		sessions = result.scalars().all()
		for session in sessions:
			if isinstance(session.symptoms, dict):
				session.symptoms = session.symptoms.get('items', [])
		return success_response(sessions, 'Recommendation history loaded')
	except Exception as exc:
		raise HTTPException(status_code=500, detail=f'Unable to load recommendation history: {exc}')


@router.get('/{id}')
async def get_rec(id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
	try:
		try:
			rec_id = uuid.UUID(id)
		except ValueError:
			raise HTTPException(status_code=400, detail='Invalid recommendation id')
		result = await db.execute(select(RecommendationSession).where(RecommendationSession.id == rec_id, RecommendationSession.user_id == current_user.id))
		session = result.scalars().first()
		if not session:
			raise HTTPException(status_code=404)
		if isinstance(session.symptoms, dict):
			session.symptoms = session.symptoms.get('items', [])
		return success_response(session, 'Recommendation loaded')
	except HTTPException:
		raise
	except Exception as exc:
		raise HTTPException(status_code=500, detail=f'Unable to load recommendation: {exc}')


@router.delete('/{id}')
async def delete_rec(id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
	try:
		try:
			rec_id = uuid.UUID(id)
		except ValueError:
			raise HTTPException(status_code=400, detail='Invalid recommendation id')
		result = await db.execute(select(RecommendationSession).where(RecommendationSession.id == rec_id, RecommendationSession.user_id == current_user.id))
		session = result.scalars().first()
		if not session:
			raise HTTPException(status_code=404)
		await db.delete(session)
		await db.commit()
		return success_response({'status': 'deleted'}, 'Recommendation deleted')
	except HTTPException:
		raise
	except Exception as exc:
		await db.rollback()
		raise HTTPException(status_code=500, detail=f'Unable to delete recommendation: {exc}')


@router.post('/prevention')
async def prevention(data: dict, request: Request, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
	location = data.get('location', 'India')
	risk_score = int(data.get('risk_score', 50))
	age_group = data.get('age_group', 'adult')
	dosha = data.get('dosha', 'vata')
	try:
		profile_res = await db.execute(select(PrakritiProfile).where(PrakritiProfile.user_id == current_user.id).order_by(PrakritiProfile.completed_at.desc()))
		profile = profile_res.scalars().first()
		if profile:
			dosha = profile.dominant_dosha
		language = resolve_language(request, current_user.language)
		plan = await recommendation_service.generate_prevention_plan(
			location=location,
			risk_score=risk_score,
			dosha=dosha,
			season=ws.get_current_season(),
			language=language,
		)
		return success_response({'plan': plan}, 'Prevention plan generated')
	except Exception as exc:
		raise HTTPException(status_code=500, detail=f'Unable to generate prevention plan: {exc}')


@router.post('/prevention-plan')
async def prevention_plan(data: dict, request: Request, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
	return await prevention(data=data, request=request, current_user=current_user, db=db)


@router.post('/arogya-report')
async def arogya_report(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
	try:
		profile = await db.scalar(
			select(PrakritiProfile)
			.where(PrakritiProfile.user_id == current_user.id)
			.order_by(PrakritiProfile.completed_at.desc())
		)
		history_rows = (
			await db.scalars(
				select(RecommendationSession)
				.where(RecommendationSession.user_id == current_user.id)
				.order_by(RecommendationSession.created_at.desc())
				.limit(10)
			)
		).all()

		history_payload = [
			{
				'date': str(row.created_at.date()) if row.created_at else '',
				'symptoms': row.symptoms,
				'response': row.response_json,
			}
			for row in history_rows
		]

		dosha = profile.dominant_dosha if profile else 'vata'
		risk = float(profile.risk_score) if profile else 50.0
		pdf_base64 = pdf_service.generate_arogya_report(
			user_name=current_user.display_name,
			dosha=dosha,
			history=history_payload,
			risk_score=risk,
		)
		return success_response({'pdf_base64': pdf_base64}, 'Arogya report generated')
	except Exception as exc:
		raise HTTPException(status_code=500, detail=f'Unable to generate Arogya report: {exc}')
