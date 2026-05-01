from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Repo(Base):
    __tablename__ = "repos"

    id = Column(Integer, primary_key=True, index=True)
    github_repo_name = Column(String, unique=True, nullable=False) 
    github_webhook_secret = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    reviews = relationship("PRReview", back_populates="repo")