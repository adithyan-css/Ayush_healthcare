import uuid
from datetime import datetime
from sqlalchemy import String, JSON, DateTime, ForeignKey, func, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING, Dict, Any
from app.database import Base

if TYPE_CHECKING:
    from app.models.user import User

class RecommendationSession(Base):
    __tablename__ = "recommendation_sessions"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    
    symptoms: Mapped[Dict[str, Any]] = mapped_column(JSON)
    free_text: Mapped[str] = mapped_column(String, nullable=True)
    season: Mapped[str] = mapped_column(String, index=True)
    response_json: Mapped[Dict[str, Any]] = mapped_column(JSON)
    prevention_plan: Mapped[str] = mapped_column(String, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="sessions")
