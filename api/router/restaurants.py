import os, random, shutil, json
from fastapi import APIRouter,Depends,HTTPException,status, UploadFile, File, Form,Request,Query
from core.database import get_db, Base
# from core.redis import save_otp, verify_otp, redis_client
from sqlalchemy.orm import Session
from schemas import *
from models import *
from utils.jwt import Hash, verify_access_token
from utils.pagination import pagination
from typing import List,Optional


router = APIRouter(tags=["Resturent"])
UPLOAD_DIR = "uploads/resturents"

@router.post("/register-resturent")
def register(request:register_resturent,db: Session = Depends(get_db),current_user:userProfile=Depends(verify_access_token)):

    # filepath = os.path.join(UPLOAD_DIR,request.resturent_name,profile_pic.filename)
    # os.makedirs(os.path.dirname(filepath), exist_ok=True)

    # with open(filepath, "wb") as buffer:
    #     shutil.copyfileobj(profile_pic.file, buffer)
    current_userr= db.query(User).filter(User.id == current_user["user_id"]).first()
    
    if not current_userr.user_role==UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Only admin can allow to create n register Resturent")
     
    new_resturent = Resturants(resturant_name =request.resturent_name, 
                               resturant_owner_id=current_user["user_id"], 
                               resturant_type=request.resturent_type, 
                               resturant_description=request.resturant_description)

    db.add(new_resturent)
    db.commit()
    db.refresh(new_resturent)
    
    return {"data",new_resturent}

@router.post("/register-resturent-img")
def add_img(
    image_url: UploadFile = File(...),
    db: Session = Depends(get_db),current_user:userProfile=Depends(verify_access_token)
):

    filepath = os.path.join(UPLOAD_DIR,image_url.filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(image_url.file, buffer)
    
    owner = db.query(Resturants).filter(Resturants.resturant_owner_id == current_user["user_id"]).first()
    if not owner:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="only Admin can Access")
       
    resturent_img = Resturent_image(
        resturant_id=owner.id,
        image_url=filepath
    )
    # print(Resturent_image.resturant_id)
    # print(id)
    
    if resturent_img.resturant_id != owner.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="resturent not created for this id")

    db.add(resturent_img)
    db.commit()
    db.refresh(resturent_img)
    
    return {"message": "image added successfully",
            "data": {
                "id":resturent_img.id,
                "resturant_id":resturent_img.resturant_id,
                "image_url":resturent_img.image_url                
            }}
    
@router.get("/resturent",response_model=PaginationResponse[RestaurantResponse])
def get_resturents(page:int = Query(1, ge=1),limit:int = Query(10, ge=1, le=100),
                   sort_by:str=Query("id"),order_by:str=Query("asc"),db:Session=Depends(get_db)):
    
    sorting_field = {
        "id":Resturants.id,
        "name":Resturants.resturant_name,
    }
    
    if sort_by not in sorting_field:
        raise HTTPException(status_code=400, detail="Invalied sorting Field")
    
    query = sorting_field[sort_by]
    
    if order_by == "asc":
        resturent = db.query(Resturants).order_by(query.asc())
    
    else:
        resturent = db.query(Resturants).order_by(query.desc())
    
    if not resturent.all():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="resturent not created for this id")
    
    # data=[]
    # for r in resturent:
    #     data.append({
    #             "id":r.id,
    #             "resturant_name":r.resturant_name,
    #             "resturant_owner_name":r.resturant_owner_id,
    #             "resturant_type": r.resturant_type,
    #             "resturant_description":r.resturant_description,
    #             "image":r.image,
    #             "Time":r.resturant_time           
    #         })
    return pagination(resturent,page,limit)

@router.get("/resturent/{id}",response_model=RestaurantResponse)
def get_resturent(id:int, db:Session=Depends(get_db)):
    resturent = db.query(Resturants).filter(Resturants.id == id)
    
    if not resturent.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="resturent not created for this id")
    
    return resturent.first()

@router.put("/resturent",response_model=update_resturent)
def updatee_resturent(request:update_resturent, db:Session=Depends(get_db),current_user:userProfile=Depends(verify_access_token)):
    
    owner = db.query(Resturants).filter(Resturants.resturant_owner_id == current_user["user_id"]).first()
    if not owner:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="only Admin with register resturent can Access")
    
    resturent = db.query(Resturants).filter(Resturants.id == owner.id)
    if not resturent.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="resturent not created for this id")

    data = request.model_dump(exclude_unset=True)

    for key, value in data.items():
        setattr(owner, key, value)
    db.commit()
    
    return resturent.first()
    # return {"data":{
    #     "resturant_name":resturent.first().resturant_name,
    #     "resturant_type":resturent.first().resturant_type,
    #     "resturant_description":resturent.first().resturant_description,
    #     "is_active":resturent.first().is_active
    #     }}

@router.get("/resturent-img/{id}",response_model=List[RestaurantImageResponse])
def get_resturent_img(id:int,request:Request, db:Session=Depends(get_db)):
    resturent = db.query(Resturent_image).filter(Resturants.id == id)
    query =  resturent.first()
    if not resturent.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="resturent not created for this id")
    
    image_url1 = None
    if query.image_url:
        image_url1=str(request.base_url)+query.image_url.lstrip("/")
         
    return resturent

@router.post("/add-time")
def add_resturent_time(request:add_time, db:Session=Depends(get_db),current_user:userProfile=Depends(verify_access_token)):
    
    owner = db.query(Resturants).filter(Resturants.resturant_owner_id == current_user["user_id"]).first()
    if not owner:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="only Admin can Access")
    
    new_time = Resturant_time(day=request.day, 
                              resturant_open_time=request.resturant_open_time, 
                              resturant_close_time=request.resturant_close_time, 
                              resturent_id=owner.id)
    # print(new_time.resturent_id)
    restaurant = db.query(Resturants).filter(Resturants.id == new_time.resturent_id).first()
    # print(restaurant.id)
    if new_time.resturent_id != restaurant.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= "resturent id not found in db")
    
    db.add(new_time)
    db.commit()
    db.refresh(new_time)
    return new_time

@router.get("/resturent-time/{id}",response_model=List[update_time])
def get_resturent_time(id:int, db:Session=Depends(get_db)):
    resturent = db.query(Resturant_time).filter(Resturant_time.resturent_id == id)
    if not resturent.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="resturent not created for this id")
    
    return resturent

@router.put("/update_time/{id}")
def update_resturent_time(id:int, request:update_time, db:Session=Depends(get_db),current_user:userProfile=Depends(verify_access_token)):

    owner = db.query(Resturants).filter(Resturants.resturant_owner_id == current_user["user_id"]).first()
    if not owner:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="only Admin can Access")
    
    query = db.query(Resturant_time).filter(Resturant_time.id==id, Resturant_time.resturent_id == owner.id ).first()
    if not query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="not found")


    data = request.model_dump(exclude_unset=True)

    for key, value in data.items():
        setattr(query, key, value)
    db.commit()
    return {"message":"time updated"}
    
@router.delete("/delete-time/{id}")
def delete_resturent_time(id:int, db:Session=Depends(get_db),current_user:userProfile=Depends(verify_access_token)):
    
    owner = db.query(Resturants).filter(Resturants.resturant_owner_id == current_user["user_id"]).first()
    if not owner:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="only Admin can Access")
    
    query = db.query(Resturant_time).filter(Resturant_time.id==id, Resturant_time.resturent_id == owner.id)
    if not query.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="not found")
    query.delete(synchronize_session=False)
    db.commit()
    
    return{"message": "time deleted" }

@router.get("/restayrents")
def search_restaurent(request: str | None=None, 
                      page:int =Query(1, ge=1),limit:int=Query(10, ge=1, le=100),db:Session=Depends(get_db)):
    
    offset=(page-1)*limit
    query=db.query(Resturants).filter(Resturants.is_active == True)
    if request:
        query=query.filter( Resturants.resturant_name.ilike(f"%{request}%"))
    
    total = query.count()
    restaurants = query.offset(offset).limit(limit).all()        
    return {
        "page": page,
        "limit": limit,
        "total_query": total,
        "total_pages": (total + limit - 1) // limit,
        "data": restaurants
    }
    