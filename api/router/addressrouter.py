from fastapi import APIRouter,Depends,HTTPException,status
from core.database import get_db
# from core.redis import save_otp, verify_otp, redis_client
from sqlalchemy.orm import Session
from schemas import *
from models import *
from utils.jwt import verify_access_token
from typing import List

router = APIRouter(tags= ["Address"])

@router.post("/add-address")
def add_address(request:Add_Address, db:Session=Depends(get_db), current_user: userProfile=Depends(verify_access_token)):
        
    new_address = Address(customer_id = current_user["user_id"],
                          name=request.name, 
                          number= request.number, 
                          address_line_1= request.address_line_1, 
                          address_line_2=request.address_line_2,
                          city=request.city, state =request.state, pincode = request.pincode)
    
    db.add(new_address)
    db.commit()
    db.refresh(new_address)
    
    return {"message":"Address Added successfully",
            "data":new_address}
    
@router.get("/get-address")
def get_address(db:Session=Depends(get_db), current_user:userProfile=Depends(verify_access_token)):
    
    query= db.query(Address).filter(Address.customer_id == current_user["user_id"])
    
    if not query.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="address not added yet")
    
    address= db.query(Address).filter(Address.customer_id == current_user["user_id"]).all()
    return address

@router.put("/update-address/{id}")
def update_address(id:int, request:Update_Address, db:Session=Depends(get_db), current_user:userProfile=Depends(verify_access_token)):
    
    query = db.query(Address).filter(Address.id == id)
    if not query.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="invalied address id")
    
    auth_address = db.query(Address).filter(Address.id == id, Address.customer_id==current_user["user_id"])
    if not auth_address.first():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="you have not access for this address id")
    auth_address.update(request.model_dump(exclude_unset=True),synchronize_session=False)
    db.commit()
    
    return {"message": "Address Updated SuccessFully"}

@router.delete("/delete-address/{id}")
def delete_address(id:int, db:Session=Depends(get_db), current_user:userProfile=Depends(verify_access_token)):

    query = db.query(Address).filter(Address.id == id)
    if not query.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="invalied address id")
    
    auth_address = db.query(Address).filter(Address.id == id, Address.customer_id==current_user["user_id"])
    if not auth_address.first():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="you have not access for this address id")
    auth_address.delete(synchronize_session=False)
    db.commit()
    return {"message": "Address Updated SuccessFully"}