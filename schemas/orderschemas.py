from pydantic import BaseModel
from decimal import Decimal

class CheckoutRequest(BaseModel):
    cart_id: int
    address_id: int
    
class Add_Order(BaseModel):
    resturant_id:int
    address_id:int
    delivery_fee:Decimal
    delivery_name:str
    delivery_number:str
    delivery_address:str
    delivery_city:str
    delivery_state:str
    delivery_pincode:str
    class Config:
        from_attributes = True
        
class Add_Order_Item(BaseModel):
    order_id:int
    food_id:int
    food_name:int
    price:float
    quantity:int
      
    class Config:
        from_attributes = True  


    