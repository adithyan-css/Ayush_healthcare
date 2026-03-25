import uuid
from datetime import datetime, timedelta

import bcrypt
from jose import jwt

from app.config import settings


class AuthService:
    def hash_password(self, password: str) -> str:
        password_bytes = password.encode('utf-8')[:72]
        return bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode('utf-8')

    def verify_password(self, plain_password: str, password_hash: str) -> bool:
        return bcrypt.checkpw(plain_password.encode('utf-8')[:72], password_hash.encode('utf-8'))

    def create_access_token(self, data: dict) -> str:
        payload = data.copy()
        payload.update(
            {
                'exp': datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
                'type': 'access',
            }
        )
        return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

    def create_refresh_token(self, data: dict) -> str:
        payload = data.copy()
        payload.update(
            {
                'exp': datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
                'type': 'refresh',
            }
        )
        return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

    def generate_local_identity(self) -> str:
        return f'local_{uuid.uuid4().hex}'
