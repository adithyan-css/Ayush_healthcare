import uuid
from fastapi import Depends, HTTPException
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


async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
	try:
		try:
			is_blacklisted = await redis_client.get(f'blacklist:{token}')
			if is_blacklisted:
				raise HTTPException(status_code=401, detail='Token blacklisted')
		except Exception:
			pass

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
