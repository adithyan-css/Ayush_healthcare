from typing import Optional
import logging
from fastapi import APIRouter, Depends, HTTPException
from jose import JWTError, jwt, ExpiredSignatureError
from pydantic import BaseModel
from sqlalchemy import text
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


async def _ensure_password_hash_column(db: AsyncSession) -> None:
	try:
		await db.execute(text('ALTER TABLE users ADD COLUMN password_hash VARCHAR'))
		await db.commit()
	except Exception:
		await db.rollback()


class RefreshRequest(BaseModel):
	refresh_token: str


class FirebaseVerifyRequest(BaseModel):
	id_token: Optional[str] = None
	firebase_uid: Optional[str] = None
	email: Optional[str] = None
	display_name: Optional[str] = None
	language: Optional[str] = None


class UpdateMeRequest(BaseModel):
	display_name: Optional[str] = None
	language: Optional[str] = None


def create_access_token(data: dict):
	return auth_service.create_access_token(data)


def create_refresh_token(data: dict):
	return auth_service.create_refresh_token(data)


@router.post('/register')
async def register(payload: AuthRegisterRequest, db: AsyncSession = Depends(get_db)):
	await _ensure_password_hash_column(db)
	result = await db.execute(select(User).where(User.email == payload.email.lower().strip()))
	existing = result.scalars().first()
	if existing:
		raise HTTPException(status_code=409, detail='Email already registered')

	new_user = User(
		firebase_uid=auth_service.generate_local_firebase_uid(),
		email=payload.email.lower().strip(),
		display_name=payload.display_name.strip(),
		password_hash=auth_service.hash_password(payload.password),
		language=payload.language,
		role='patient',
	)
	db.add(new_user)
	await db.commit()
	await db.refresh(new_user)

	access_token = create_access_token(data={'sub': str(new_user.id)})
	refresh_token = create_refresh_token(data={'sub': str(new_user.id)})
	return success_response({'access_token': access_token, 'refresh_token': refresh_token, 'token_type': 'bearer'}, 'Registered successfully')


@router.post('/login')
async def login(payload: AuthLoginRequest, db: AsyncSession = Depends(get_db)):
	await _ensure_password_hash_column(db)
	result = await db.execute(select(User).where(User.email == payload.email.lower().strip()))
	user = result.scalars().first()
	if not user or not user.password_hash:
		raise HTTPException(status_code=401, detail='Invalid email or password')

	if not auth_service.verify_password(payload.password, user.password_hash):
		raise HTTPException(status_code=401, detail='Invalid email or password')

	access_token = create_access_token(data={'sub': str(user.id)})
	refresh_token = create_refresh_token(data={'sub': str(user.id)})
	return success_response({'access_token': access_token, 'refresh_token': refresh_token, 'token_type': 'bearer'}, 'Login successful')


@router.post('/firebase-verify')
async def firebase_verify(payload: FirebaseVerifyRequest, db: AsyncSession = Depends(get_db)):
	await _ensure_password_hash_column(db)

	verified_uid = ''
	verified_email = ''
	verified_name = ''

	if payload.id_token:
		try:
			verified = auth_service.verify_firebase_token(payload.id_token)
			verified_uid = verified.get('uid', '')
			verified_email = verified.get('email', '')
			verified_name = verified.get('name', '')
		except Exception as exc:
			raise HTTPException(status_code=401, detail=str(exc))
	else:
		verified_uid = (payload.firebase_uid or '').strip()
		verified_email = (payload.email or '').strip().lower()
		verified_name = (payload.display_name or '').strip()
		if not verified_uid or not verified_email:
			raise HTTPException(status_code=400, detail='firebase_uid and email required when id_token is absent')

	if not verified_uid:
		verified_uid = auth_service.generate_local_firebase_uid()
	if not verified_email:
		verified_email = f'{verified_uid}@firebase.local'
	if not verified_name:
		verified_name = verified_email.split('@')[0]

	try:
		result = await db.execute(select(User).where(User.firebase_uid == verified_uid))
		user = result.scalars().first()

		if not user:
			by_email = await db.execute(select(User).where(User.email == verified_email))
			user = by_email.scalars().first()

		if not user:
			user = User(
				firebase_uid=verified_uid,
				email=verified_email,
				display_name=verified_name,
				language=payload.language or 'en',
				role='patient',
			)
			db.add(user)
		else:
			user.firebase_uid = verified_uid
			user.email = verified_email
			user.display_name = verified_name or user.display_name
			if payload.language:
				user.language = payload.language

		await db.commit()
		await db.refresh(user)
		access_token = create_access_token(data={'sub': str(user.id)})
		refresh_token = create_refresh_token(data={'sub': str(user.id)})
		return success_response({'access_token': access_token, 'refresh_token': refresh_token, 'token_type': 'bearer'}, 'Firebase verified')
	except Exception as exc:
		await db.rollback()
		raise HTTPException(status_code=500, detail=f'Firebase verification failed: {exc}')


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
