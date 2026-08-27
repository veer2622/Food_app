from core.database import Base
from sqlalchemy import Column,Integer,String,Boolean,DateTime,Enum,ForeignKey,Numeric,Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from enum import Enum as PyEnum


class PaymentMethod(PyEnum):
    COD = "COD"
    MOCK_ONLINE = "MOCK_ONLINE"


class PaymentStatus(PyEnum):
    PENDING = "PENDING"
    PAID = "PAID"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"


class Payment(Base):

    __tablename__ = "payments"
    
    id = Column(Integer,primary_key=True,index=True)
    order_id = Column(Integer,ForeignKey("orders.id"),nullable=False,unique=True,index=True)
    amount = Column(Numeric(10, 2),nullable=False)
    payment_method = Column(Enum(PaymentMethod),nullable=False)
    status = Column(Enum(PaymentStatus),nullable=False,default=PaymentStatus.PENDING)
    transaction_id = Column(String(100),nullable=True,unique=True)
    created_at = Column(DateTime,default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime,default=lambda: datetime.now(timezone.utc),onupdate=lambda: datetime.now(timezone.utc))
    order = relationship("Order",back_populates="payment") 