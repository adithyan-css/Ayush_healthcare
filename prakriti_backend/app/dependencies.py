from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models.user import User
import redis.asyncio as redis
from app.config import settings
from jose import jwt, JWTError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/v1/auth/firebase-verify')
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)


async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
	try:
		is_blacklisted = await redis_client.get(f'blacklist:{token}')
		if is_blacklisted:
			raise HTTPException(status_code=401, detail='Token blacklisted')
		payload = jwt.decode(token, settings.JWT_SECRET, algorithms=['HS256'])
		user_id = payload.get('sub')
		if not user_id:
			raise HTTPException(status_code=401, detail='Invalid token payload')
		result = await db.execute(select(User).where(User.id == user_id))
		user = result.scalars().first()
		if not user:
			raise HTTPException(status_code=401, detail='User not found')
		return user
	except JWTError:
		raise HTTPException(status_code=401, detail='Invalid credentials')
