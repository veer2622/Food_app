from core.database import Base
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from datetime import datetime,timezone
from enum import Enum as pyEnum


class Review(Base):

    __tablename__ = "reviews"
    __table_args__ = (CheckConstraint("rating >= 1 AND rating <= 5",name="check_rating_range"),)

    id = Column(Integer,primary_key=True,index=True)
    customer_id = Column(Integer,ForeignKey("users.id"),nullable=False)
    restaurant_id = Column(Integer,ForeignKey("resturants.id"),nullable=False)
    food_id = Column(Integer,ForeignKey("food.id"),nullable=True)
    rating = Column(Integer,nullable=False)
    comment = Column(Text,nullable=True)
    created_at = Column(DateTime,default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime,default=lambda: datetime.now(timezone.utc),onupdate=lambda: datetime.now(timezone.utc))
    customer = relationship("User",back_populates="reviews")
    restaurant = relationship("Resturants",back_populates="reviews")
    food = relationship("Food",back_populates="reviews")