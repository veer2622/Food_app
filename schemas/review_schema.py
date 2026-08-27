from pydantic import BaseModel

class RestaurantReviewRequest(BaseModel):
    restaurant_id:int
    rating:int
    comment:str | None = None

class FoodReviewRequest(BaseModel):
    restaurant_id:int
    food_id:int
    rating:int
    comment:str | None = None
    
class ReviewUpdateRequest(BaseModel):
    rating:int  | None = None
    comment:str | None = None