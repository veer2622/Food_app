import os, random, shutil, json
from fastapi import APIRouter,Depends,HTTPException,status, UploadFile, File, Form,Request
from core.get_current_user import get_current_customer
from core.database import get_db, Base
# from core.redis import save_otp, verify_otp, redis_client
from sqlalchemy.orm import Session
from schemas import *
from models import *
from utils.jwt import Hash, verify_access_token
from typing import List
from sqlalchemy import func
from decimal import Decimal

router = APIRouter(tags= ["Cart"])

@router.post("/add-cart")
def add_cart( db:Session=Depends(get_db), current_user:userProfile=Depends(verify_access_token)):

    customer = get_current_customer(db, current_user)
    
    cart=db.query(Cart).filter(Cart.customer_id== customer.id,Cart.status == CartStatus.ACTIVE).first()
    if cart:
        raise HTTPException(status_code=400, detail="Cart already exists for this user")
    
    new_cart=Cart(customer_id = customer.id, status = CartStatus.ACTIVE)
    db.add(new_cart)
    db.commit()
    db.refresh(new_cart)

    return {
        "message": "Cart created successfully",
        "cart_id": new_cart.id,
        "customer_id": new_cart.customer_id,
        "status": new_cart.status
    }
    
@router.post("/add_to Cart")
def add_to_cart(request:Add_Cart_Item, db:Session=Depends(get_db), current_user:userProfile=Depends(verify_access_token)):

    customer= get_current_customer(db, current_user)
    
    if request.quantity <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Quantity must be greater than zero")

    food = db.query(Food).filter(Food.id == request.food_id).first()
    if not food:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="food not found")
    
    cart = db.query(Cart).filter(Cart.id == request.cart_id, 
                                Cart.customer_id == customer.id, 
                                Cart.status == CartStatus.ACTIVE).first()
    
    if not cart:
        cart=Cart(customer_id = customer.id, status = CartStatus.ACTIVE)
        db.add(cart)
        db.commit()
        db.refresh(cart)

    cart_item = db.query(Cart_Item).filter(
    Cart_Item.cart_id == cart.id,
    Cart_Item.food_id == food.id,
    Cart_Item.is_deleted == False
    ).first()
    
    if cart_item:

        cart_item.quantity += request.quantity
        cart_item.total = (Decimal(str(food.food_price))* cart_item.quantity)

    else:
        total_price = (Decimal(str(food.food_price))* request.quantity)   
            
        cart_item = Cart_Item(
            cart_id=cart.id,
            food_id=food.id,
            quantity=request.quantity,
            total=total_price
        )
        db.add(cart_item)

    db.commit()
    db.refresh(cart_item)
        
    
    return {
        "message": "Item added to cart successfully",
        "cart_item_id": cart_item.id,
        "cart_id": cart_item.cart_id,
        "food_id": cart_item.food_id,
        "food_name": food.food_name,
        "food_price": food.food_price,
        "quantity": cart_item.quantity,
        "total": cart_item.total
    }
    
@router.patch("/cart/items/{cart_item_id}/remove")
def remove_from_cart(cart_item_id: int,request:Remove_Cart_Item, db:Session=Depends(get_db), current_user:userProfile=Depends(verify_access_token)):

    customer= get_current_customer(db, current_user)

    if request.quantity <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Quantity must be greater than zero")

    cart_item = db.query(Cart_Item).join(Cart).filter(Cart_Item.id == cart_item_id,
                                            Cart.customer_id == customer.id,
                                            Cart.status == CartStatus.ACTIVE,
                                            Cart_Item.is_deleted == False).first()

    if not cart_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found")
    
    if request.quantity > cart_item.quantity:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot remove more quantity than available in cart")

    food = db.query(Food).filter(Food.id == cart_item.food_id).first()
    if not food:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Food not found for the cart item")


    if request.quantity == cart_item.quantity:
        cart_item.is_deleted = True
        cart_item.quantity = 0
        cart_item.total = Decimal("0.00")

    else:
        cart_item.quantity -= request.quantity
        cart_item.total = (Decimal(str(food.food_price))* cart_item.quantity)

    db.commit()
    db.refresh(cart_item)
        
    return {
        "message": "Cart updated successfully",
        "cart_item_id": cart_item.id,
        "quantity": cart_item.quantity,
        "total": cart_item.total
    }

@router.get("/cart")
def get_cart(db: Session = Depends(get_db), current_user: userProfile = Depends(verify_access_token)):

    customer = get_current_customer(db, current_user)

    cart = db.query(Cart).filter(Cart.customer_id == customer.id,Cart.status == CartStatus.ACTIVE).first()

    if not cart:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Cart not found")

    cart_items = db.query(Cart_Item).filter(Cart_Item.cart_id == cart.id,Cart_Item.is_deleted == False).all()

    items = []
    cart_total = Decimal("0.00")

    for item in cart_items:

        food = db.query(Food).filter(Food.id == item.food_id).first()

        if not food:
            continue

        cart_total += item.total

        items.append({
            "cart_item_id": item.id,
            "food_id": food.id,
            "food_name": food.food_name,
            "food_price": food.food_price,
            "quantity": item.quantity,
            "total": item.total
        })

    return {
        "cart_id": cart.id,
        "customer_id": customer.id,
        "status": cart.status,
        "items": items,
        "total_items": len(items),
        "cart_total": cart_total
    }

@router.delete("/cart-item/{cart_item_id}")
def delete_cart(cart_item_id:int, db:Session=Depends(get_db), current_user:userProfile=Depends(verify_access_token)):
    
    customer= get_current_customer(db, current_user)

    cart_item = db.query(Cart_Item).join(Cart).filter(
        Cart_Item.id == cart_item_id,
        Cart.customer_id == customer.id,
        Cart.status == CartStatus.ACTIVE,
        Cart_Item.is_deleted == False).first()

    if not cart_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found")

    cart_item.is_deleted = True
    cart_item.quantity = 0
    cart_item.total = Decimal("0.00")
    db.commit()

    return {"message": "Cart item deleted successfully"}

    
    