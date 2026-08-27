from core.database import Base
from sqlalchemy import Column,String,Integer,Boolean,DateTime,Enum,Text, Time, ForeignKey,UniqueConstraint
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from datetime import datetime, timezone, timedelta

class category(PyEnum):
    indian = "Indian"
    chinese="Chinese"
    italian="Italian"
    south_indian = "South Indian"
    north_indian = "North Indian"
    fast_food="Fast Food"
    desserts="Desserts"
    biryani="Biryani"
    pizza="Pizza"
    beverages="Beverages"
    
    
class daies(PyEnum):
    sunday="SUnday"
    monday="Monday"
    tuesday= "Tuesday"
    wednesday="Wednesday"
    thursday="Thursday"
    friday="Friday"
    saturday="Saturday"

class Resturants(Base):
    __tablename__ = "resturants"
    
    id=Column(Integer,primary_key=True, index=True)
    resturant_name = Column(String(200),nullable=False)
    resturant_owner_id=Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False )
    resturant_type=Column(Enum(category), nullable=False)
    resturant_description=Column(Text)
    is_approve=Column(Boolean, default=True)
    is_active=Column(Boolean, default=True)
    created_at=Column(DateTime,default=lambda: datetime.now(timezone.utc))
    updated_at=Column(DateTime,default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    owner = relationship("User", back_populates="resturent")
    image = relationship("Resturent_image", back_populates="resturent",cascade="all, delete-orphan")
    resturant_time=relationship("Resturant_time", back_populates="resturent",cascade="all, delete-orphan")
    food =relationship("Food", back_populates="resturent")
    orders = relationship("Order",back_populates="restaurant")
    reviews = relationship("Review",back_populates="restaurant")
    fav_restaurent = relationship("Favorite_Restaurent", back_populates="restaurant")
    
class Resturant_time(Base):
    __tablename__ = "resturant_time"
    __table_args__ = (UniqueConstraint("resturent_id","day",name="unique_restaurant_day"),)
    
    id = Column(Integer,primary_key=True)
    day = Column(Enum(daies),nullable=False)
    resturant_open_time=Column(Time)
    resturant_close_time=Column(Time)
    resturent_id = Column(Integer, ForeignKey("resturants.id"))
    resturent = relationship("Resturants", back_populates="resturant_time")  
    
    
class Resturent_image(Base):
    __tablename__ = "images"
    __table_args__ = (UniqueConstraint("resturant_id","image_url",name="unique_resturent_img"),)
    
    id =Column(Integer,primary_key=True, index=True)
    image_url = Column(String, nullable=False)
    resturant_id = Column(Integer, ForeignKey("resturants.id"))
    resturent = relationship("Resturants", back_populates="image")
    is_approve=Column(Boolean, default=True)
    is_active=Column(Boolean, default=True)
    created_at=Column(DateTime,default=lambda: datetime.now(timezone.utc))
    updated_at=Column(DateTime,default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    