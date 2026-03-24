from sqlalchemy import Column, Integer, String, Boolean, Float
from app.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    uid = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    is_active = Column(Boolean, default=True)

class PrakritiProfile(Base):
    __tablename__ = "prakriti_profiles"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    vata_score = Column(Float)
    pitta_score = Column(Float)
    kapha_score = Column(Float)
    dominant_dosha = Column(String)

class RecommendationSession(Base):
    __tablename__ = "recommendation_sessions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    session_data = Column(String)
    created_at = Column(String)

class DistrictRisk(Base):
    __tablename__ = "district_risks"
    id = Column(Integer, primary_key=True, index=True)
    state_id = Column(String)
    district_id = Column(String)
    risk_level = Column(String)
    dominant_symptom = Column(String)

class HrvReading(Base):
    __tablename__ = "hrv_readings"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    hrv_value = Column(Float)
    timestamp = Column(String)
