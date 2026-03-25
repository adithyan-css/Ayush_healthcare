from typing import Optional
import logging
from fastapi import APIRouter, Depends, HTTPException
from jose import JWTError, jwt, ExpiredSignatureError
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.dependencies import get_current_user, oauth2_scheme, redis_client, success_response, serialize_user
from app.config import settings
from app.models.user import User
from app.schemas.schemas import AuthRegisterRequest, AuthLoginRequest
from app.services.auth_service import AuthService

router = APIRouter()
auth_service = AuthService()
logger = logging.getLogger('prakriti_backend')


def _resolve_role(email: str) -> str:
	return 'doctor' if email.lower().strip() in settings.doctor_emails_set else 'patient'


class RefreshRequest(BaseModel):
	refresh_token: str


class UpdateMeRequest(BaseModel):
	display_name: Optional[str] = None
	language: Optional[str] = None


def create_access_token(data: dict):
	return auth_service.create_access_token(data)


def create_refresh_token(data: dict):
	return auth_service.create_refresh_token(data)


@router.post('/register')
async def register(payload: AuthRegisterRequest, db: AsyncSession = Depends(get_db)):
	result = await db.execute(select(User).where(User.email == payload.email.lower().strip()))
	existing = result.scalars().first()
	if existing:
		raise HTTPException(status_code=409, detail='Email already registered')

	new_user = User(
		firebase_uid=auth_service.generate_local_identity(),
		email=payload.email.lower().strip(),
		display_name=payload.display_name.strip(),
		password_hash=auth_service.hash_password(payload.password),
		language=payload.language,
		role=_resolve_role(payload.email),
	)
	db.add(new_user)
	await db.commit()
	await db.refresh(new_user)

	access_token = create_access_token(data={'sub': str(new_user.id)})
	refresh_token = create_refresh_token(data={'sub': str(new_user.id)})
	return success_response({'access_token': access_token, 'refresh_token': refresh_token, 'token_type': 'bearer'}, 'Registered successfully')


@router.post('/login')
async def login(payload: AuthLoginRequest, db: AsyncSession = Depends(get_db)):
	result = await db.execute(select(User).where(User.email == payload.email.lower().strip()))
	user = result.scalars().first()
	if not user or not user.password_hash:
		raise HTTPException(status_code=401, detail='Invalid email or password')

	if not auth_service.verify_password(payload.password, user.password_hash):
		raise HTTPException(status_code=401, detail='Invalid email or password')

	expected_role = _resolve_role(user.email)
	if user.role != expected_role:
		user.role = expected_role
		await db.commit()
		await db.refresh(user)

	access_token = create_access_token(data={'sub': str(user.id)})
	refresh_token = create_refresh_token(data={'sub': str(user.id)})
	return success_response({'access_token': access_token, 'refresh_token': refresh_token, 'token_type': 'bearer'}, 'Login successful')

@router.post('/refresh')
async def refresh(payload: RefreshRequest):
	try:
		decoded = jwt.decode(payload.refresh_token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
		if decoded.get('type') != 'refresh':
			raise HTTPException(status_code=401, detail='Invalid refresh token type')
		sub = decoded.get('sub')
		if not sub:
			raise HTTPException(status_code=401, detail='Invalid refresh token')
		token = create_access_token(data={'sub': sub})
		return success_response({'access_token': token, 'token_type': 'bearer'}, 'Token refreshed')
	except ExpiredSignatureError:
		raise HTTPException(status_code=401, detail='Refresh token expired')
	except JWTError:
		raise HTTPException(status_code=401, detail='Invalid refresh token')


@router.post('/logout')
async def logout(token: str = Depends(oauth2_scheme)):
	try:
		await redis_client.setex(f'blacklist:{token}', 3600, 'true')
	except Exception as exc:
		logger.warning('Failed to blacklist token during logout: %s', exc)
	return success_response({}, 'Logged out successfully')


@router.get('/me')
async def get_me(current_user: User = Depends(get_current_user)):
	return success_response(serialize_user(current_user), 'Current user loaded')


@router.put('/me')
async def update_me(payload: UpdateMeRequest, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
	try:
		if payload.display_name is not None:
			current_user.display_name = payload.display_name
		if payload.language is not None:
			current_user.language = payload.language
		await db.commit()
		await db.refresh(current_user)
		return success_response(serialize_user(current_user), 'Profile updated')
	except Exception as exc:
		await db.rollback()
		raise HTTPException(status_code=500, detail=f'Profile update failed: {exc}')
