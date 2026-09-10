import os, random, shutil, json, re
from fastapi import APIRouter,Depends,HTTPException,status, UploadFile, File, Form, Request
from core.database import get_db, Base
from core.redis import save_otp, verify_otp, redis_client
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from schemas import *
from models import *
from utils.jwt import Hash,create_access_token, verify_access_token
from typing import List,Optional
from pydantic import Field, field_validator


router = APIRouter(tags=["User"])

def generate_otp():
    return str(random.randint(100000,999999))

UPLOAD_DIR = "uploads/profile"
os.makedirs(UPLOAD_DIR, exist_ok=True)

#--------------------------------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------------------------------
# for number validation     
def validate_number(number:str):

    if not re.search(r"\d{10}$", number):
        raise HTTPException(status_code=400, detail="only write number and its 10 digit long") 
           
#--------------------------------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------------------------------
# for password validation     
def validate_password(password: str):
    if len(password) < 12:
        raise HTTPException(
            status_code=400,
            detail="Password must be at least 12 characters long")

    if not re.search(r"[A-Z]", password):
        raise HTTPException(
            status_code=400,
            detail="Password must contain at least one uppercase letter"
        )

# re regular expresion
    if not re.search(r"[a-z]", password):
        raise HTTPException(
            status_code=400,
            detail="Password must contain at least one lowercase letter"
        )

    if not re.search(r"\d", password):
        raise HTTPException(
            status_code=400,
            detail="Password must contain at least one number"
        )

    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        raise HTTPException(
            status_code=400,
            detail="Password must contain at least one special character"
        )

#--------------------------------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------------------------------


@router.post("/register")
def register(
    name: str = Form(...),
    number: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    profile_pic: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
):

    validate_number(number)
    validate_password(password)

    existing_user = db.query(User).filter(User.number == number).first()   
    if existing_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Register With same number not allow")

    existing_user = db.query(User).filter(User.email == email).first()   
    if existing_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Register With same email not allow")

    if profile_pic:
        pic= profile_pic.filename
    else:
        pic = None

    otp = generate_otp()

    save_otp(email, otp)

    user_data = {
        "name": name,
        "number": number,
        "email": email,
        "password": password,
        "profile_pic": pic
    }

    redis_client.set(
        f"pending:{email}",
        json.dumps(user_data),
        ex=600
    )


    return {"message": "OTP sent on ur email"}

@router.post("/verify")
def verify_registration(request:verify_user,db: Session = Depends(get_db)):

    is_valid = verify_otp(request.email, request.otp)
    
    if not is_valid:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired OTP"
        )

    # Get temporary user data
    data = redis_client.get(f"pending:{request.email}")

    if not data:
        raise HTTPException(
            status_code=400,
            detail="Registration expired"
        )

    user_data = json.loads(data)


    # Step 3: Save the uploaded file
    if user_data['profile_pic'] != None:    
        filepath = os.path.join(UPLOAD_DIR,user_data["name"],user_data["profile_pic"])
    else:
        filepath= None

    # with open(filepath, "wb") as buffer:
    #     shutil.copyfileobj(profile_pic.file, buffer)

    # Create user
    new_user = User(
        user_role=UserRole.CUSTOMER,
        name=user_data["name"],
        number=user_data["number"],
        email=user_data["email"],
        password=Hash.hashing(user_data["password"]),
        profile_pic=filepath,
    )


    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    redis_client.delete(f"pending:{request.email}")
        
    return {
        "message": "Registration Done",
        "data": new_user
    }

@router.post("/admin")
def admin_register(
    name: str = Form(...),
    number: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    profile_pic: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
):

    validate_number(number)
    validate_password(password)

    existing_user = db.query(User).filter(User.number == number).first()   
    if existing_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Register With same number not allow")

    existing_user = db.query(User).filter(User.email == email).first()   
    if existing_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Register With same email not allow")

    if profile_pic:
        pic= profile_pic.filename
    else:
        pic = None

    otp = generate_otp()

    save_otp(email, otp)

    user_data = {
        "name": name,
        "number": number,
        "email": email,
        "password": password,
        "profile_pic": pic
    }

    redis_client.set(
        f"pending:{email}",
        json.dumps(user_data),
        ex=600
    )


    return {"message": "OTP sent on ur email"}

@router.post("/verify-")
def verify_registration(request:verify_user,db: Session = Depends(get_db)):

    is_valid = verify_otp(request.email, request.otp)
    
    if not is_valid:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired OTP"
        )

    # Get temporary user data
    data = redis_client.get(f"pending:{request.email}")

    if not data:
        raise HTTPException(
            status_code=400,
            detail="Registration expired"
        )

    user_data = json.loads(data)


    # Step 3: Save the uploaded file
    if user_data['profile_pic'] != None:    
        filepath = os.path.join(UPLOAD_DIR,user_data["name"],user_data["profile_pic"])
    else:
        filepath= None

    # with open(filepath, "wb") as buffer:
    #     shutil.copyfileobj(profile_pic.file, buffer)

    # Create user
    new_user = User(
        user_role=UserRole.ADMIN,
        name=user_data["name"],
        number=user_data["number"],
        email=user_data["email"],
        password=Hash.hashing(user_data["password"]),
        profile_pic=filepath,
    )


    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    redis_client.delete(f"pending:{request.email}")
        
    return {
        "message": "Registration Done",
        "data": new_user
    }



# @router.post("/register-user")
# def register_user(
#     name: str = Form(...),
#     number: str = Form(...),
#     email: str = Form(...),
#     password: str = Form(...),
#     profile_pic: Optional[UploadFile] = File(None),
#     # profile_pic: UploadFile = File(...),
#     db: Session = Depends(get_db),
# ):

#     validate_number(number)
#     validate_password(password)
#     if profile_pic:
#         filepath = os.path.join(UPLOAD_DIR,name,profile_pic.filename)
#         os.makedirs(os.path.dirname(filepath), exist_ok=True)

#         with open(filepath, "wb") as buffer:
#             shutil.copyfileobj(profile_pic.file, buffer)
#     else:
#         filepath =  None            
#     try:
#         existing_user = db.query(User).filter(User.number == number).first()
           
#         if existing_user:
#             raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Register With same number not allow")
   
#         new_user = User(
#             user_role=UserRole.CUSTOMER,
#             name=name,
#             number=number,
#             email=email,
#             password=Hash.hashing(password),
#             profile_pic=filepath
#         )

#         db.add(new_user)
#         db.commit()
#         db.refresh(new_user)
        
#     except IntegrityError:
#         db.rollback()

#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="This number is already registered"
#         )
        
#     return new_user

# @router.post("/admin1")
# def register_admin(
#     name: str = Form(...),
#     number: str = Form(...),
#     email: str = Form(...),
#     password: str = Form(...),
#     profile_pic: UploadFile = File(...),
#     db: Session = Depends(get_db),
# ):

#     validate_number(number)
#     validate_password(password)
#     filepath = os.path.join(UPLOAD_DIR,name,profile_pic.filename)
#     os.makedirs(os.path.dirname(filepath), exist_ok=True)

#     with open(filepath, "wb") as buffer:
#         shutil.copyfileobj(profile_pic.file, buffer)
#     try:
#         existing_user = db.query(User).filter(User.number == number).first()
           
#         if existing_user:
#             raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Register With same number not allow")
    
#         new_user = User(
#             user_role=UserRole.ADMIN,
#             name=name,
#             number=number,
#             email=email,
#             password=Hash.hashing(password),
#             profile_pic=filepath
#         )

#         db.add(new_user)
#         db.commit()
#         db.refresh(new_user)
        
#     except IntegrityError:
#         db.rollback()

#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="This number is already registered"
#         )
    
#     return new_user
 
@router.post("/login")
def login(request:login_responce, db:Session=Depends(get_db)):
    user = db.query(User).filter(User.email==request.username).first()
        
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")
    
    if not Hash.verify(request.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalied  password")
    
    if user.is_active==False:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not active")
     
    # if not user.user_role== UserRole.CUSTOMER:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only Registered Customer Allow")  
    
    access_token = create_access_token(data={"sub":user.email, "user_id":user.id})
    return {"access_token":access_token, "token_type":"bearer"}
    
    
@router.get("/user_profile")
def user_profile(request:Request,db:Session=Depends(get_db) ,current_user:userProfile=Depends(verify_access_token)):
    profile = db.query(User).filter(User.id == current_user["user_id"]).first()
    
    if not profile:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Customer access required")

    image_url = None
    if profile.profile_pic:
        image_url=str(request.base_url)+profile.profile_pic.lstrip("/")
         
    
    return {"data":profile, "profile_pic":image_url}

@router.put("/user_profile/")
def update_user_profile(request:delete_user ,db:Session=Depends(get_db), current_user:userresponce=Depends(verify_access_token)):
    profile = db.query(User).filter(User.id == current_user["user_id"], User.user_role == UserRole.CUSTOMER)
    
    user = profile.first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found") 
    
    profile.update(request.model_dump(), synchronize_session=False)
    db.commit()
    
    return {"message": "Profile Updated Successfully"}

@router.delete("/user_profile")
def delete_user_profile(db:Session=Depends(get_db), current_user:userresponce=Depends(verify_access_token)):
    profile = db.query(User).filter(User.id == current_user["user_id"])
    user = profile.first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")
    
    # profile.delete(synchronize_session=False)
    user.is_active=False
    db.commit()
    
    return {"message": "Profile deleted"}



                                 