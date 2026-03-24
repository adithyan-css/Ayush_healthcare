from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, JSON, func
from app.database import Base

class RecommendationSession(Base):
    __tablename__ = "recommendation_sessions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    symptoms = Column(JSON)
    free_text = Column(String)
    season = Column(String)
    response_json = Column(JSON)
    prevention_plan = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())\n