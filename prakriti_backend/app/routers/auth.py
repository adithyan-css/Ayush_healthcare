from datetime import datetime, timedelta
from typing import Dict, Optional
from fastapi import APIRouter, Depends, HTTPException
from jose import JWTError, jwt
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.config import settings
from app.database import get_db
from app.dependencies import get_current_user, oauth2_scheme, redis_client
from app.models.user import User
from app.schemas.schemas import UserResponse

router = APIRouter()


class RefreshRequest(BaseModel):
	refresh_token: str


class UpdateMeRequest(BaseModel):
	display_name: Optional[str] = None
	language: Optional[str] = None


def create_access_token(data: dict):
	to_encode = data.copy()
	expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
	to_encode.update({'exp': expire, 'type': 'access'})
	return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(data: dict):
	to_encode = data.copy()
	expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
	to_encode.update({'exp': expire, 'type': 'refresh'})
	return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


@router.post('/firebase-verify')
async def verify(data: Dict, db: AsyncSession = Depends(get_db)):
	try:
		firebase_uid = data.get('firebase_uid', 'mock_uid')
		email = data.get('email', 'mock@example.com')
		display_name = data.get('display_name', 'User')
		result = await db.execute(select(User).where(User.firebase_uid == firebase_uid))
		user = result.scalars().first()
		if not user:
			user = User(firebase_uid=firebase_uid, email=email, display_name=display_name)
			db.add(user)
			await db.commit()
			await db.refresh(user)
		access_token = create_access_token(data={'sub': str(user.id)})
		refresh_token = create_refresh_token(data={'sub': str(user.id)})
		return {'access_token': access_token, 'refresh_token': refresh_token, 'token_type': 'bearer'}
	except Exception as exc:
		raise HTTPException(status_code=500, detail=f'Auth verification failed: {exc}')


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
		return {'access_token': token, 'token_type': 'bearer'}
	except JWTError:
		raise HTTPException(status_code=401, detail='Invalid refresh token')


@router.post('/logout')
async def logout(token: str = Depends(oauth2_scheme)):
	try:
		await redis_client.setex(f'blacklist:{token}', 3600, 'true')
	except Exception:
		pass
	return {'msg': 'Logged out successfully'}


@router.get('/me', response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
	return current_user


@router.put('/me', response_model=UserResponse)
async def update_me(payload: UpdateMeRequest, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
	try:
		if payload.display_name is not None:
			current_user.display_name = payload.display_name
		if payload.language is not None:
			current_user.language = payload.language
		await db.commit()
		await db.refresh(current_user)
		return current_user
	except Exception as exc:
		await db.rollback()
		raise HTTPException(status_code=500, detail=f'Profile update failed: {exc}')
