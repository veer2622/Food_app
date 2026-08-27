from core.database import Base
from sqlalchemy import Column,Integer,String,Boolean,DateTime,Enum,ForeignKey,Numeric,Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from enum import Enum as PyEnum
from models.payment import PaymentStatus, PaymentMethod


class OrderStatus(PyEnum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    PREPARING = "PREPARING"
    READY = "READY"
    OUT_FOR_DELIVERY = "OUT_FOR_DELIVERY"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"

class Order(Base):

    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer,ForeignKey("users.id"),nullable=False,index=True)
    restaurant_id = Column(Integer,ForeignKey("resturants.id"),nullable=False,index=True)
    address_id = Column(Integer,ForeignKey("addresses.id"),nullable=False,index=True)
    status = Column(Enum(OrderStatus),nullable=False,default=OrderStatus.PENDING,index=True)
    payment_status = Column(Enum(PaymentStatus),nullable=False,default=PaymentStatus.PENDING,index=True)
    subtotal = Column(Numeric(10, 2),nullable=False)
    # tax = Column(Numeric(10, 2),nullable=False,default=0)
    delivery_fee = Column(Numeric(10, 2),nullable=False,default=0)
    total_amount = Column(Numeric(10, 2),nullable=False)
    delivery_name = Column(String(255),nullable=False)
    delivery_number = Column(String(15),nullable=False)
    delivery_address = Column(Text,nullable=False)
    delivery_city = Column(String(100),nullable=False)
    delivery_state = Column(String(100),nullable=False)
    delivery_pincode = Column(String(10),nullable=False)
    created_at = Column(DateTime,default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime,default=lambda: datetime.now(timezone.utc),onupdate=lambda: datetime.now(timezone.utc))

    customers = relationship("User",back_populates="orders")
    restaurant = relationship("Resturants",back_populates="orders")
    address = relationship("Address",back_populates="orders")
    order_items = relationship("Order_Item",back_populates="order",cascade="all, delete-orphan")
    payment = relationship("Payment",back_populates="order",uselist=False,cascade="all, delete-orphan")
    
    # @property
    # def subtotal(self):
    #     return sum(
    #         item.subtotal or 0
    #         for item in self.order_items
    #     )
    
    # @property
    # def total_amount(self):
    #     return (self.subtotal or 0) + (self.delivery_fee or 0) 
     
class Order_Item(Base):

    __tablename__ = "order_items"

    id = Column(Integer,primary_key=True,index=True)
    order_id = Column(Integer,ForeignKey("orders.id"),nullable=False,index=True)
    food_id = Column(Integer,ForeignKey("food.id"),nullable=False,index=True)
    food_name = Column(String(100),nullable=False)
    price = Column(Numeric(10, 2),nullable=False)
    quantity = Column(Integer,nullable=False)
    subtotal = Column(Numeric(10, 2),nullable=False)
    created_at = Column(DateTime,default=lambda: datetime.now(timezone.utc))
    order = relationship("Order",back_populates="order_items")
    food = relationship("Food",back_populates="order_items")