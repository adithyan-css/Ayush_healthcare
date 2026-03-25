import uuid
import logging
from fastapi import Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models.user import User
import redis.asyncio as redis
from app.config import settings
from jose import jwt, JWTError, ExpiredSignatureError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/v1/auth/login')
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
logger = logging.getLogger('prakriti_backend')


def success_response(data=None, message: str = 'Success'):
	return {'success': True, 'data': data if data is not None else {}, 'message': message}


def error_response(message: str, data=None):
	return {'success': False, 'data': data if data is not None else {}, 'message': message}


def serialize_user(user: User) -> dict:
	return {
		'id': str(user.id),
		'email': user.email,
		'display_name': user.display_name,
		'role': user.role,
		'language': user.language,
		'created_at': user.created_at.isoformat() if user.created_at else None,
		'updated_at': user.updated_at.isoformat() if user.updated_at else None,
	}


def normalize_language_code(code: str | None) -> str:
	if not code:
		return 'en'
	lowered = str(code).strip().lower()
	if lowered in {'en', 'english'}:
		return 'en'
	if lowered in {'ta', 'tamil'}:
		return 'ta'
	if lowered in {'hi', 'hindi'}:
		return 'hi'
	if lowered in {'te', 'telugu'}:
		return 'te'
	if lowered in {'ja', 'japanese'}:
		return 'ja'
	return 'en'


def resolve_language(request: Request | None = None, user_language: str | None = None) -> str:
	if request is not None:
		header_value = request.headers.get('x-language') or request.headers.get('accept-language')
		if header_value:
			return normalize_language_code(header_value.split(',')[0])
	return normalize_language_code(user_language)


async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
	try:
		try:
			is_blacklisted = await redis_client.get(f'blacklist:{token}')
			if is_blacklisted:
				raise HTTPException(status_code=401, detail='Token blacklisted')
		except Exception as exc:
			logger.warning('Redis blacklist check failed: %s', exc)

		payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
		if payload.get('type') not in (None, 'access'):
			raise HTTPException(status_code=401, detail='Invalid token type')
		user_id = payload.get('sub')
		if not user_id:
			raise HTTPException(status_code=401, detail='Invalid token payload')
		try:
			user_uuid = uuid.UUID(str(user_id))
		except Exception:
			raise HTTPException(status_code=401, detail='Invalid token subject')

		result = await db.execute(select(User).where(User.id == user_uuid))
		user = result.scalars().first()
		if not user:
			raise HTTPException(status_code=401, detail='User not found')
		return user
	except ExpiredSignatureError:
		raise HTTPException(status_code=401, detail='Token expired')
	except JWTError:
		raise HTTPException(status_code=401, detail='Invalid credentials')
