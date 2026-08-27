from pydantic import BaseModel,ConfigDict
from enum import Enum
from datetime import time,datetime
from typing import Optional

# class Category(str, Enum):
#     fine_dining = "Fine Dining"
#     casual_dining = "Casual Dining"
#     fast_food = "Fast Food"
#     cafe = "Cafe"
#     buffet = "Buffet"
#     pubs_n_bars = "Pubs & Bars"


# class Days(str, Enum):
#     sunday = "Sunday"
#     monday = "Monday"
#     tuesday = "Tuesday"
#     wednesday = "Wednesday"
#     thursday = "Thursday"
#     friday = "Friday"
#     saturday = "Saturday"
    

class register_resturent(BaseModel):
    resturent_name:str
    resturent_type:str
    resturant_description:str
    
    class Config():
        from_attributes = True

class update_resturent(BaseModel):

    resturant_name:str  | None = None
    resturant_type:str  | None = None
    resturant_description:str | None = None
    is_active:bool | None = None
    
    class Config():
        from_attributes = True

        
class   update_time(BaseModel):
    day:str | None = None
    resturant_open_time:time | None = None
    resturant_close_time:time | None = None
    

class add_time(BaseModel):
    day:str
    resturant_open_time:time
    resturant_close_time:time
    class Config():
        from_attributes = True
        
class resturent_times(BaseModel):
    resturent_id:int
    resturant_time:list[update_time]=[]
    class Config():
        from_attributes = True


class add_image(BaseModel):
    
    image_url:str
    resturant_id:int
    
    
class RestaurantImageResponse(BaseModel):
    
    # id: int
    # image_name: str | None = None
    image_url: str | None = None
    resturant_id:int | None = None
    # is_primary: bool
    # created_at: datetime

    class Config():
        from_attributes = True

class ImageResponse(BaseModel):
    image_url: str | None = None

class RestaurantResponse(BaseModel):
    id: int
    resturant_name: str
    resturant_owner_id: int
    resturant_type: str
    resturant_description: str | None = None
    is_approve: bool
    is_active: bool
    image: list[ImageResponse]=[]
    resturant_time:list[update_time]=[]


    model_config = ConfigDict(from_attributes=True)
    


class RestaurantListResponse(BaseModel):
    items: list[RestaurantResponse]
    total: int
    page: int
    size: int
    pages: int