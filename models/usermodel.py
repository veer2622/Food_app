from core.database import Base
from sqlalchemy import Column, Integer, String, Boolean, DateTime,Enum
from sqlalchemy.orm import relationship
from datetime import datetime,timezone
from enum import Enum as pyEnum


# def password_validator(cls, password:str) -> str:
#     if len(password)<11:
#         raise ValueError("Password must me 12 degit Long")
    
#     for char in password:
#         if not any(char.isdigit):
#             raise ValueError("take atleast one digit in ur password")
        
#         if not any(char.isupper):
#             raise ValueError("Take Atleast one Upper case")

class UserRole(pyEnum):
    CUSTOMER = "CUSTOMER"
    ADMIN = "ADMIN"
    
            
class User(Base):
    __tablename__  = "users"
    
    id=Column(Integer,primary_key=True)
    user_role=Column(Enum(UserRole), nullable=False)
    name = Column(String(200))
    number = Column(String(15), unique=True,nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    profile_pic = Column(String(255), nullable=True)
    password = Column(String(1000))
    # otp = Column(String(6), nullable=True)
    # otp_expire = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    is_active = Column(Boolean, default=True)
    is_varified = Column(Boolean, default=True)
    resturent = relationship("Resturants", back_populates="owner",passive_deletes=True)
    cart =relationship("Cart", back_populates="customers")
    addresses = relationship("Address",back_populates="customers",cascade="all, delete-orphan")
    orders = relationship("Order",back_populates="customers")
    reviews = relationship("Review",back_populates="customer")
    fav_food = relationship("Favorite_Food", back_populates="customer")
    fav_restaurent = relationship("Favorite_Restaurent", back_populates="customer")
