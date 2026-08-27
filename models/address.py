from core.database import Base
from sqlalchemy import Column,Integer,String,Boolean,DateTime,ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone


class Address(Base):

    __tablename__ = "addresses"

    id = Column(Integer,primary_key=True,index=True)

    customer_id = Column(Integer,ForeignKey("users.id"),nullable=False,index=True)
    name = Column(String(200),nullable=False)
    number = Column(String(15),nullable=False)
    address_line_1 = Column(String(500),nullable=False)
    address_line_2 = Column(String(500),nullable=True)
    city = Column(String(100),nullable=False)
    state = Column(String(100),nullable=False)
    pincode = Column(String(10),nullable=False)
    is_default = Column(Boolean,default=False)
    created_at = Column(DateTime,default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime,default=lambda: datetime.now(timezone.utc),onupdate=lambda: datetime.now(timezone.utc))
    
    customers = relationship("User",back_populates="addresses")
    orders = relationship("Order",back_populates="address")