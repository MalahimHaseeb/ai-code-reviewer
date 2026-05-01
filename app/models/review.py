from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class PRReview(Base):
    __tablename__ = "pr_reviews"

    id = Column(Integer, primary_key=True, index=True)
    repo_id = Column(Integer, ForeignKey("repos.id"), nullable=False)
    pr_number = Column(Integer, nullable=False)
    pr_title = Column(String, nullable=False)
    diff = Column(Text, nullable=False)       
    ai_review = Column(Text, nullable=True)  
    status = Column(String, default="pending") 
    created_at = Column(DateTime, default=datetime.utcnow)

    repo = relationship("Repo", back_populates="reviews")