import uuid
from datetime import datetime
from sqlalchemy import String, Float, DateTime, ForeignKey, func, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING
from app.database import Base

if TYPE_CHECKING:
	from app.models.user import User


class PrakritiProfile(Base):
	__tablename__ = 'prakriti_profiles'
	id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4, index=True)
	user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('users.id', ondelete='CASCADE'), index=True)
	vata_score: Mapped[float] = mapped_column(Float)
	pitta_score: Mapped[float] = mapped_column(Float)
	kapha_score: Mapped[float] = mapped_column(Float)
	dominant_dosha: Mapped[str] = mapped_column(String, index=True)
	risk_score: Mapped[float] = mapped_column(Float, default=0.0)
	completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
	updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
	user: Mapped['User'] = relationship('User', back_populates='profiles')
