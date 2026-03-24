import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, func, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, TYPE_CHECKING
from app.database import Base

if TYPE_CHECKING:
	from app.models.prakriti import PrakritiProfile
	from app.models.recommendation import RecommendationSession
	from app.models.hrv import HrvReading
	from app.models.symptom import SymptomReport


class User(Base):
	__tablename__ = 'users'
	id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4, index=True)
	firebase_uid: Mapped[str] = mapped_column(String, unique=True, index=True)
	email: Mapped[str] = mapped_column(String, unique=True, index=True)
	display_name: Mapped[str] = mapped_column(String)
	password_hash: Mapped[str] = mapped_column(String, nullable=True)
	role: Mapped[str] = mapped_column(String, default='patient')
	language: Mapped[str] = mapped_column(String, default='en')
	created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
	updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
	profiles: Mapped[List['PrakritiProfile']] = relationship('PrakritiProfile', back_populates='user', cascade='all, delete-orphan')
	sessions: Mapped[List['RecommendationSession']] = relationship('RecommendationSession', back_populates='user', cascade='all, delete-orphan')
	hrv_readings: Mapped[List['HrvReading']] = relationship('HrvReading', back_populates='user', cascade='all, delete-orphan')
	symptom_reports: Mapped[List['SymptomReport']] = relationship('SymptomReport', back_populates='user', cascade='all, delete-orphan')
