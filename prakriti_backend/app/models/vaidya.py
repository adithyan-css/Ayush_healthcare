import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import DateTime, ForeignKey, JSON, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
	from app.models.user import User


class VaidyaConsult(Base):
	__tablename__ = 'vaidya_consults'
	id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4, index=True)
	doctor_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('users.id', ondelete='CASCADE'), index=True)
	patient_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('users.id', ondelete='CASCADE'), index=True)
	symptoms: Mapped[list[str]] = mapped_column(JSON)
	suggestion_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
	outcome_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
	status: Mapped[str] = mapped_column(String, default='suggested', index=True)
	created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
	updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

	doctor: Mapped['User'] = relationship('User', foreign_keys=[doctor_id], back_populates='doctor_consults')
	patient: Mapped['User'] = relationship('User', foreign_keys=[patient_id], back_populates='patient_consults')
