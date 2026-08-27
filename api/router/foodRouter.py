import os, random, shutil, json
from fastapi import APIRouter,Depends,HTTPException,status, UploadFile, File, Form,Request, Query
from fastapi_filter import FilterDepends
from core.database import get_db
from core.get_current_user import get_current_customer
# from core.redis import save_otp, verify_otp, redis_client
from sqlalchemy.orm import Session
from sqlalchemy import select
from schemas import *
from models import *
from utils.jwt import verify_access_token
from typing import List
from fastapi_pagination import Page, add_pagination, paginate   


router = APIRouter(tags=["Food"])
add_pagination(router)

UPLOAD_DIR = "uploads/Food"

@router.post("/Add-Food")
def add_food(request:Add_Food, db:Session=Depends(get_db),current_user:userProfile=Depends(verify_access_token)):
    
    owner = db.query(Resturants).filter(Resturants.resturant_owner_id == current_user["user_id"]).first()
    if not owner:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="only Admin with resturent  can Access")
    
    new_food = Food(food_name=request.food_name,
        food_category=request.food_category,
        food_description=request.food_description,
        food_price=request.food_price,
        resturent_id = owner.id
        )
    
    
    db.add(new_food)
    db.commit()
    db.refresh(new_food)
    
    return{"message":"Food Added Successfully","data":new_food}

@router.get("/Get-Food")
def get_foods(db:Session=Depends(get_db)):
    food = db.query(Food).all()
    
    if not food:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    data =[]
    
    for f in food:
        if f.is_activated == False:
            continue
        data.append(f)
    
    return data

@router.put("/update_food/{id}")
def update_food(id:int, request:Update_Food, db:Session=Depends(get_db),current_user:userProfile=Depends(verify_access_token)):

    owner = db.query(Resturants).filter(Resturants.resturant_owner_id == current_user["user_id"]).first()
    if not owner:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="only Admin can Access")
    
    query=db.query(Food).filter(Food.id == id, Food.resturent_id == owner.id).first()
    
    if not query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    

    data = request.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(query,key,value)
    db.commit()
    
    return{"message":"Food Updated Successfully"}

@router.put("/delete-reactive-food/{id}")
def delete__reactive_food(id:int, request:Delete_Food, db:Session=Depends(get_db),current_user:userProfile=Depends(verify_access_token)):
    
    owner = db.query(Resturants).filter(Resturants.resturant_owner_id == current_user["user_id"]).first()
    if not owner:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="only Admin can Access")
        
    query= db.query(Food).filter(Food.id == id, Food.resturent_id == owner.id)
    deleted_food = query.first()
    if not deleted_food:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    query.update(request.model_dump(),synchronize_session=False)
    db.commit()
    
    # if deleted_food.is_activated==True:
    #     return{"message": "Food reactive Successfully"}
        
    # if deleted_food.is_activated==False:
    #     return{"message": "Food deleted Successfully"}
    
    return{"message": "Food reactive Successfully" if deleted_food.is_activated==True else "Food deleted Successfully"}
    

@router.post("/add-food-image")
def add_food_image(request:Request, food_image_name:str = Form(...),
                   food_image_url:UploadFile=File(...),
                   food_id:int =Form(...), 
                   db:Session=Depends(get_db),current_user:userProfile=Depends(verify_access_token)):
    

    filepath = os.path.join(UPLOAD_DIR,food_image_name,food_image_url.filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(food_image_url.file, buffer)

    owner = db.query(Resturants).filter(Resturants.resturant_owner_id == current_user["user_id"]).first()
    if not owner:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="only Admin can Access")
    
    query=db.query(Food).filter(Food.id == food_id, Food.resturent_id == owner.id)
    if not query.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Food for available for this id")
    
    new_food = Food_Image(food_image_name=food_image_name,food_image_url=filepath,food_id=food_id)
    db.add(new_food)
    db.commit()
    db.refresh(new_food)
    
    return{"message": "Food_image added Successfully", 
            "data": {
                "id": new_food.id,
                "food_image_name": new_food.food_image_name,
                "food_id": new_food.food_id,
                "image_url": str(request.base_url) +new_food.food_image_url.lstrip("/")
                }
            }


@router.get("/get-food-images")
def get_food_images(
    request: Request,
    db: Session = Depends(get_db)
):
    food_images = db.query(Food_Image).all()

    data = []

    for image in food_images:
        data.append({
            "id": image.id,
            "food_image_name": image.food_image_name,
            "food_id": image.food_id,
            "image_url": str(request.base_url) +
                         image.food_image_url.lstrip("/")
        })

    return {
        "message": "Food images fetched successfully",
        "data": data
    }

@router.get("/get-food-image/{image_id}")
def get_food_image(image_id: int,request: Request,db: Session = Depends(get_db)):
    food_image = db.query(Food_Image).filter(Food_Image.id == image_id).first()

    if not food_image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Food image not found"
        )

    return {
        "message": "Food image fetched successfully",
        "data": {
            "id": food_image.id,
            "food_image_name": food_image.food_image_name,
            "food_id": food_image.food_id,
            "image_url": str(request.base_url) +
                         food_image.food_image_url.lstrip("/")
        }
    }

@router.put("/update-food-image/{image_id}")
def update_food_image(
    image_id: int,
    request: Request,
    food_image_name: str = Form(...),
    food_image_url: UploadFile = File(...),
    food_id: int = Form(...),
    db: Session = Depends(get_db),current_user:userProfile=Depends(verify_access_token)
):

    owner = db.query(Resturants).filter(Resturants.resturant_owner_id == current_user["user_id"]).first()
    if not owner:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="only Admin can Access")

    food = db.query(Food).filter(Food.id == food_id, Food.resturent_id == owner.id).first()
    if not food:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Food not available for this id"
        )

    food_image = db.query(Food_Image).filter(Food_Image.id == image_id, Food_Image.food_id == food.id).first()
    if not food_image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Food image not found for this Food"
        )

    if food_image.food_image_url:
        old_filepath = food_image.food_image_url

        if os.path.exists(old_filepath):
            os.remove(old_filepath)

    filepath = os.path.join(UPLOAD_DIR,food_image_name,food_image_url.filename)
    os.makedirs(os.path.dirname(filepath),exist_ok=True)

    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(food_image_url.file,buffer)
        
    food_image.food_image_name = food_image_name
    food_image.food_image_url = filepath
    food_image.food_id = food_id

    db.commit()
    db.refresh(food_image)

    return {
        "message": "Food image updated successfully",
        "data": food_image,
        "image_url": str(request.base_url) + food_image.food_image_url.lstrip("/")
    }


@router.delete("/delete-food-image/{image_id}")
def delete_food_image(image_id: int, db: Session = Depends(get_db),current_user:userProfile=Depends(verify_access_token)):

    owner = db.query(Resturants).filter(Resturants.resturant_owner_id == current_user["user_id"]).first()
    if not owner:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="only Admin can Access")
    
    food = db.query(Food).filter(Food.resturent_id == owner.id).first()
    if not food:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="only Admin can Access this Food ")    
    
    food_image = db.query(Food_Image).filter(Food_Image.id == image_id, Food_Image.food_id == food.id).first()

    if not food_image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Food image not found"
        )

    if food_image.food_image_url:
        filepath = food_image.food_image_url

        if os.path.exists(filepath):
            os.remove(filepath)

    db.delete(food_image)
    db.commit()

    return {
        "message": "Food image deleted successfully"
    }


@router.get("/food")
def search_foods(request: str | None=None,
                page:int=Query(1,ge=1), limit:int=Query(1,ge=1, le=100), db:Session=Depends(get_db)):
    
    offset=(page-1)*limit
    total = db.query(Food).count()
    
    
    
    if request:
        foods = db.query(Food).filter(Food.is_activated == True, 
                                                  Food.food_name.ilike(f"%{request}%") ).offset(offset).limit(limit).all()
        
        return foods
    else:
        foods = db.query(Food).filter(Food.is_activated == True).offset(offset).limit(limit).all()
        return foods  

@router.get("/foods")
def get_foods(food_filter:FoodFilter = FilterDepends(FoodFilter), db:Session = Depends(get_db)):
    query = select(Food)
    query = food_filter.filter(query) 
    result = db.execute(query)
    return result.scalars().all()


@router.post("/make-fav-food")
def add_to_fav_food(request:Favorite_food, db:Session=Depends(get_db), current_user:userProfile=Depends(verify_access_token)):
    
    customer= get_current_customer(db, current_user)
    
    food = db.query(Food).filter(Food.id == request.food_id, Food.is_activated == True).first()
    if not food:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="food not found ")
    
    fav_food = Favorite_Food(user_id= customer.id, food_id=food.id)
    db.add(fav_food)
    db.commit()
    db.refresh(fav_food)
    
    return fav_food

@router.post("/unlike-fav-food")
def remove_from_fav_food(request:Favorite_food, db:Session=Depends(get_db), current_user:userProfile=Depends(verify_access_token)):
    
    customer= get_current_customer(db, current_user)
    
    food = db.query(Food).filter(Food.id == request.food_id, Food.is_activated == True).first()
    if not food:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="food not found ")
    
    fav_food = db.query(Favorite_Food).filter(Favorite_Food.food_id == food.id, Favorite_Food.user_id == customer.id).first()
    if not fav_food:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="item is not in ur favorite list ")
    fav_food.is_favorite = False
    fav_food.is_active = False
    fav_food.is_delete = True
    
    db.commit()
    return {"message": "food_unluke successfully"}


@router.get("/get-fav-food")
def get_fav_food(db:Session=Depends(get_db), current_user:userProfile=Depends(verify_access_token)):
    
    customer= get_current_customer(db, current_user)
    
    fav_food = db.query(Favorite_Food).join(Food).filter(Favorite_Food.user_id == customer.id,Food.is_activated==True,
                                              Favorite_Food.is_favorite==True, Favorite_Food.is_active == True).all()
    
    return fav_food
