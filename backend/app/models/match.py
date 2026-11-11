from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, Text, String
from sqlalchemy.orm import relationship
from app.database import Base


class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    requirement_id = Column(Integer, ForeignKey("buyer_requirements.id", ondelete="CASCADE"), nullable=False, index=True)
    listing_id = Column(Integer, ForeignKey("waste_listings.id", ondelete="CASCADE"), nullable=False, index=True)
    
    total_score = Column(Float, nullable=False)  # 0.0 - 100.0 score
    score_breakdown = Column(Text, nullable=True)  # JSON explaining material, distance, quantity, price score
    status = Column(String(50), default="proposed")  # proposed, accepted, declined
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    requirement = relationship("BuyerRequirement", back_populates="matches")
    listing = relationship("WasteListing")
