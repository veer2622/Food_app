from core.database import Base
from sqlalchemy import Column, Integer, String, Boolean, DateTime,Enum, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime,timezone
from enum import Enum as pyEnum


class Food_Category(pyEnum):
    starters="Starters"
    soups="Soups"
    salads="Salads"
    main_course="Main Course"
    rice_and_biryani="Rice & Biryani"
    breads="Breads"
    pizza="Pizza"
    burgers="Burgers"
    pasta_and_noodles="Pasta & Noodles"
    tandoor_and_grills="Tandoor & Grills"
    desserts="Desserts"
    beverages="Beverages"
    combos="Combos"
    

class Food(Base):
    __tablename__ = "food"
    
    id=Column(Integer,primary_key=True, index=True)
    food_name=Column(String(100), index=True, nullable=False)
    food_category=Column(Enum(Food_Category), nullable=False)
    food_description= Column(String, nullable=False)
    food_price=Column(Numeric(10,2), nullable=False)      #i think remove
    is_activated = Column(Boolean, default=True, nullable=False)
    created_at=Column(DateTime, default=lambda : datetime.now(timezone.utc))
    updated_at=Column(DateTime, default=lambda : datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    resturent_id = Column(Integer, ForeignKey("resturants.id"))
    food_images = relationship("Food_Image", back_populates="food",  cascade="all, delete-orphan")
    resturent = relationship("Resturants", back_populates="food")
    cart_item =relationship("Cart_Item", back_populates="food")
    order_items = relationship("Order_Item",back_populates="food")
    reviews = relationship("Review",back_populates="food")
    fav_food = relationship("Favorite_Food", back_populates="food")
    

class Food_Image(Base):
    __tablename__ = "food_images"
    
    id=Column(Integer,primary_key=True, index=True)
    food_image_name=Column(String)
    food_image_url=Column(String, nullable=True)
    food_id=Column(Integer, ForeignKey("food.id"),nullable=False)
    created_at=Column(DateTime, default=lambda : datetime.now(timezone.utc))
    updated_at=Column(DateTime, default=lambda : datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    food = relationship("Food", back_populates="food_images")