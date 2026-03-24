import uuid
from datetime import datetime, timedelta

from jose import jwt
from passlib.context import CryptContext

from app.config import settings


class AuthService:
    def __init__(self):
        self._pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

    def hash_password(self, password: str) -> str:
        return self._pwd_context.hash(password)

    def verify_password(self, plain_password: str, password_hash: str) -> bool:
        return self._pwd_context.verify(plain_password, password_hash)

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

    def generate_local_firebase_uid(self) -> str:
        return f'local_{uuid.uuid4().hex}'
