from pydantic import BaseModel, Field

class Add_Cart(BaseModel):
    customer_id:int
    
class Add_Cart_Item(BaseModel):
    cart_id:int
    food_id:int
    quantity:int =  Field(gt=0)

class Remove_Cart_Item(BaseModel):
    quantity:int =  Field(gt=0)
    
class Updated_Cart_Item(BaseModel):
    food_id:int
    quantity:int
    
class CartItemResponse(BaseModel):
    id: int
    cart_id: int
    food_id: int
    food_name: str
    food_price: int
    quantity: int
    total: int

    class Config:
        from_attributes = True
        
class Delete_Cart_Item(BaseModel):
    cart_id:int