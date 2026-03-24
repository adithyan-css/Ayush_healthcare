import uuid
from datetime import datetime
from sqlalchemy import String, Float, DateTime, JSON, func, Uuid
from sqlalchemy.orm import Mapped, mapped_column
from typing import Dict, Any
from app.database import Base

class DistrictRisk(Base):
    __tablename__ = "district_risks"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4, index=True)
    state_code: Mapped[str] = mapped_column(String, index=True)
    state_name: Mapped[str] = mapped_column(String, index=True)
    
    risk_score: Mapped[float] = mapped_column(Float, index=True)
    risk_level: Mapped[str] = mapped_column(String, index=True)
    top_condition: Mapped[str] = mapped_column(String)
    trend: Mapped[str] = mapped_column(String)
    
    monthly_cases: Mapped[Dict[str, Any]] = mapped_column(JSON)
    seasons_map: Mapped[Dict[str, Any]] = mapped_column(JSON)
    
    latitude: Mapped[float] = mapped_column(Float, nullable=True)
    longitude: Mapped[float] = mapped_column(Float, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
