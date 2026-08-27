from core.database import Base
from sqlalchemy import Column, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime,timezone

class Favorite_Food(Base):
    __tablename__ = "fav_food"
        
    id=Column(Integer, primary_key=True)
    user_id= Column(Integer, ForeignKey("users.id"))
    food_id = Column(Integer, ForeignKey("food.id"))
    is_favorite = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    is_delete = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    customer = relationship("User", back_populates="fav_food")
    food = relationship("Food", back_populates="fav_food")
    
    

class Favorite_Restaurent(Base):
    __tablename__ = "fav_restaurent"
        
    id=Column(Integer, primary_key=True)
    user_id= Column(Integer, ForeignKey("users.id"))
    restaurent_id = Column(Integer, ForeignKey("resturants.id"))
    is_favorite = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    is_delete = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    customer = relationship("User", back_populates="fav_restaurent")
    restaurant = relationship("Resturants", back_populates="fav_restaurent")