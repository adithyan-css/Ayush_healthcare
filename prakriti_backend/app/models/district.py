from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, func
from app.database import Base

class DistrictRisk(Base):
    __tablename__ = "district_risks"
    id = Column(Integer, primary_key=True, index=True)
    state_code = Column(String, index=True)
    state_name = Column(String)
    risk_score = Column(Float)
    risk_level = Column(String)
    top_condition = Column(String)
    trend = Column(String)
    monthly_cases = Column(JSON)
    seasons_map = Column(JSON)
    latitude = Column(Float)
    longitude = Column(Float)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())\n