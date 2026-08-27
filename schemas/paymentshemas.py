from pydantic import BaseModel
from models import PaymentMethod


class PaymentRequest(BaseModel):
    order_id:int
    payment_method:PaymentMethod
    # payment_method:str