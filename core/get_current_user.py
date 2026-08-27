from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.database import get_db
from models import *
from schemas import *
from utils.jwt import verify_access_token


def get_current_customer(db: Session=Depends(get_db), current_user: userProfile=Depends(verify_access_token)):

    customer = db.query(User).filter(User.id == current_user["user_id"]).first()

    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
        detail="Customer not found")

    if customer.user_role != UserRole.CUSTOMER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
        detail="Only customers can access orders")

    return customer