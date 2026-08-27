from core.database import Base
from sqlalchemy import Column, Integer, String, Boolean, DateTime,Enum, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime,timezone
from models import *
from enum import Enum as PyEnum

class CartStatus(PyEnum):
    ACTIVE = "ACTIVE"
    CHECKED_OUT = "CHECKED_OUT"

class Cart(Base):
    __tablename__ ="carts"
    
    id = Column(Integer,primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(Enum(CartStatus),nullable=False,default=CartStatus.ACTIVE)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    cart_item = relationship("Cart_Item", back_populates="cart")
    customers = relationship("User", back_populates="cart")
    
    @property
    def total(self):
        return sum(
            item.total or 0
            for item in self.cart_item
            if not item.is_deleted
        )

class Cart_Item(Base):
    __tablename__ ="cart_items"
    
    id = Column(Integer,primary_key=True, index=True)
    cart_id = Column(Integer,ForeignKey("carts.id"), nullable=False)
    food_id = Column(Integer, ForeignKey("food.id"), nullable=False)
    quantity = Column(Integer)
    total= Column(Numeric(10,2), nullable=False, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    is_deleted = Column(Boolean, default=False)
    cart= relationship("Cart", back_populates="cart_item")
    food = relationship("Food", back_populates="cart_item")