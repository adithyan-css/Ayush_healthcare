from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, ForeignKey, func
from app.database import Base

class HrvReading(Base):
    __tablename__ = "hrv_readings"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    hrv_ms = Column(Float)
    nadi_type = Column(String)
    is_anomaly = Column(Boolean, default=False)
    measured_at = Column(DateTime(timezone=True), server_default=func.now())\n