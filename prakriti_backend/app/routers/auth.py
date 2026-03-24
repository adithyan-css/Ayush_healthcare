from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models.user import User
from app.schemas.schemas import UserCreate, UserResponse
from app.dependencies import get_current_user, redis_client, oauth2_scheme
from datetime import datetime, timedelta
from jose import jwt
from app.config import settings
from typing import Dict

router = APIRouter()

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=60)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm="HS256")

@router.post("/firebase-verify")
async def verify(data: Dict, db: AsyncSession = Depends(get_db)):
    # Mock firebase verify logic
    firebase_uid = data.get("firebase_uid", "mock_uid")
    email = data.get("email", "mock@example.com")
    display_name = data.get("display_name", "Mock User")
    
    result = await db.execute(select(User).where(User.firebase_uid == firebase_uid))
    user = result.scalars().first()
    
    if not user:
        user = User(firebase_uid=firebase_uid, email=email, display_name=display_name)
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
    token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}

@router.post("/refresh")
async def refresh(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    token = create_access_token(data={"sub": str(current_user.id)})
    return {"access_token": token, "token_type": "bearer"}

@router.post("/logout")
async def logout(token: str = Depends(oauth2_scheme)):
    await redis_client.setex(f"blacklist:{token}", 3600, "true")
    return {"msg": "Logged out successfully"}

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_me(data: Dict, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if "display_name" in data:
        current_user.display_name = data["display_name"]
    await db.commit()
    await db.refresh(current_user)
    return current_user
