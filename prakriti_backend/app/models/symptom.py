import uuid
from datetime import datetime
from sqlalchemy import Float, DateTime, ForeignKey, JSON, func, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING, Dict, Any
from app.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class SymptomReport(Base):
    __tablename__ = 'symptom_reports'
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('users.id', ondelete='CASCADE'), index=True)
    symptoms: Mapped[Dict[str, Any]] = mapped_column(JSON)
    latitude: Mapped[float] = mapped_column(Float, nullable=True)
    longitude: Mapped[float] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    user: Mapped['User'] = relationship('User', back_populates='symptom_reports')
import uuid
from datetime import datetime
from sqlalchemy import Float, DateTime, ForeignKey, JSON, func, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING, Dict, Any
from app.database import Base

if TYPE_CHECKING:
    from app.models.user import User

class SymptomReport(Base):
    __tablename__ = "symptom_reports"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    
    symptoms: Mapped[Dict[str, Any]] = mapped_column(JSON)
    latitude: Mapped[float] = mapped_column(Float, nullable=True)
    longitude: Mapped[float] = mapped_column(Float, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship("User", back_populates="symptom_reports")
