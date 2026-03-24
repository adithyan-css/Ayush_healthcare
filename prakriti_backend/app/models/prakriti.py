from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, func
from app.database import Base

class PrakritiProfile(Base):
    __tablename__ = "prakriti_profiles"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    vata_score = Column(Float)
    pitta_score = Column(Float)
    kapha_score = Column(Float)
    dominant_dosha = Column(String)
    risk_score = Column(Float)
    completed_at = Column(DateTime(timezone=True), server_default=func.now())\n