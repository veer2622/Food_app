import os, random, shutil, json, random
from fastapi import APIRouter,Depends,HTTPException,status, UploadFile, File, Form,Request, BackgroundTasks
from utils.email import send_order_confirmation_email
from core.database import get_db, Base
# from core.redis import save_otp, verify_otp, redis_client
from sqlalchemy.orm import Session
from core.get_current_user import get_current_customer
from schemas import *
from models import *
from utils.jwt import Hash, verify_access_token
from typing import List
from sqlalchemy import func
from decimal import Decimal

router = APIRouter(tags= ["Payment"])

@router.post("/make-payment")
def make_payment(request: PaymentRequest,background_tasks: BackgroundTasks,db: Session = Depends(get_db),
                 current_user: userProfile = Depends(verify_access_token)):

    try:

        current = get_current_customer(db, current_user)

        order = db.query(Order).filter(Order.id == request.order_id,Order.customer_id == current.id).first()
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Order not found")

        if order.payment_status == PaymentStatus.PAID:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Order is already paid")

        existing_payment = db.query(Payment).filter(Payment.order_id == order.id).first()

        if existing_payment:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Payment already exists for this order")

        payment = Payment(order_id=order.id,amount=order.total_amount,
                            payment_method=request.payment_method,status=PaymentStatus.PENDING)

        db.add(payment)
        db.flush()

        if request.payment_method == PaymentMethod.COD:
            payment.status = PaymentStatus.PENDING
            order.payment_status = PaymentStatus.PENDING
            order.status = OrderStatus.CONFIRMED

        elif request.payment_method == PaymentMethod.MOCK_ONLINE:
            payment.status = PaymentStatus.PAID
            payment.transaction_id = (f"MOCK-{payment.id}-{random.randint(100000, 999999)}")
            order.payment_status = PaymentStatus.PAID
            order.status = OrderStatus.CONFIRMED

        db.commit()
        db.refresh(payment)
        db.refresh(order)
        
        background_tasks.add_task(
            send_order_confirmation_email,
            current.email,
            current.name,
            order.id,
            order.total_amount
        )

        return {
            "message": "Payment processed successfully",

            "payment": {
                "payment_id": payment.id,
                "order_id": payment.order_id,
                "amount": payment.amount,
                "payment_method": payment.payment_method,
                "payment_status": payment.status,
                "transaction_id": payment.transaction_id
            },

            "order": {
                "order_id": order.id,
                "order_status": order.status,
                "payment_status": order.payment_status,
                "total_amount": order.total_amount
            }
        }

    except HTTPException:
        db.rollback()
        raise

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Payment processing failed")