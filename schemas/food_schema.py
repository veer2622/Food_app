from pydantic import BaseModel
from typing import Optional
from models import Food
from fastapi_filter import FilterDepends
from fastapi_filter.contrib.sqlalchemy import Filter
from decimal import Decimal

class Add_Food(BaseModel):
    food_name:str
    food_category:str
    food_description:str
    food_price:float
    class Config():
        from_attributes = True
            
class Update_Food(BaseModel):
    food_name:str | None = None
    food_description:str | None = None
    food_price:float | None = None
    class Config():
        from_attributes = True    

class Get_Food(BaseModel):
    id:int


class Delete_Food(BaseModel):
    is_activated:bool
    
class Add_Food_Img(BaseModel):
    food_image_name:str
    food_image:str
    food_id: int
    class Config():
        from_attributes = True

class FoodFilter(Filter):
    food_category: Optional[str] = None
    food_price__gte: Optional[Decimal] = None 
    food_price__lte: Optional[Decimal] = None
    food_name__ilike: Optional[str] = None

    class Constants(Filter.Constants):
        model = Food