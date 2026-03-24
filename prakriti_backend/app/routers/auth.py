from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.user import User
from app.schemas.schemas import UserCreate, UserResponse
from typing import Dict

router = APIRouter()

@router.post("/firebase-verify")
async def verify(data: Dict, db: AsyncSession = Depends(get_db)): return {"token": "mock_jwt_token"}

@router.post("/refresh")
async def refresh(db: AsyncSession = Depends(get_db)): return {"token": "new_mock_jwt_token"}

@router.post("/logout")
async def logout(db: AsyncSession = Depends(get_db)): return {"msg": "Logged out"}

@router.get("/me", response_model=UserResponse)
async def get_me(db: AsyncSession = Depends(get_db)): 
    # Return mock current user (in real implementation, depend on get_current_user)
    return {"id": "1", "firebase_uid": "uid123", "email": "test@test.com", "display_name": "Test", "role": "patient", "language": "en", "created_at": "2023-01-01T00:00:00Z"}

@router.put("/me")
async def update_me(db: AsyncSession = Depends(get_db)): return {"msg": "Updated"}\n