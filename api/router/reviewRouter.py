import os, random, shutil, json
from fastapi import APIRouter,Depends,HTTPException,status, UploadFile, File, Form,Request
from core.database import get_db, Base
# from core.redis import save_otp, verify_otp, redis_client
from sqlalchemy.orm import Session
from schemas import *
from models import *
from utils.jwt import Hash,create_access_token, verify_access_token
from typing import List
from sqlalchemy import func
from decimal import Decimal

router = APIRouter(tags= ["Reviews"])

@router.post("/reviews/restaurant")
def create_restaurant_review(request:RestaurantReviewRequest, db:Session = Depends(get_db), current_user:userProfile = Depends(verify_access_token)):


    customer = db.query(User).filter(User.id == current_user["user_id"]).first()
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Customer not found")
    if customer.user_role != UserRole.CUSTOMER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Only customers can create reviews")

    if request.rating < 1 or request.rating > 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Rating must be between 1 and 5")

    restaurant = db.query(Resturants).filter(Resturants.id == request.restaurant_id).first()

    if not restaurant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Restaurant not found")

    delivered_order = db.query(Order).filter(Order.customer_id == customer.id,
                                             Order.restaurant_id == restaurant.id
                                            #  Order.status == OrderStatus.DELIVERED
                                             ).first()

    if not delivered_order: 
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="You can review only a restaurant you have ordered from")

    existing_review = db.query(Review).filter(Review.customer_id == customer.id,
                                              Review.restaurant_id == restaurant.id,
                                              Review.food_id.is_(None)).first()

    if existing_review:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="You have already reviewed this restaurant")

    review = Review(customer_id=customer.id,restaurant_id=restaurant.id,
                    food_id=None,rating=request.rating,comment=request.comment)

    db.add(review)
    db.commit()
    db.refresh(review)

    return {
        "message": "Restaurant review created successfully",
        "review": {
            "id": review.id,
            "customer_id": review.customer_id,
            "restaurant_id": review.restaurant_id,
            "rating": review.rating,
            "comment": review.comment,
            "created_at": review.created_at
        }
    }
    
@router.post("/reviews/food")
def create_food_review(
    request: FoodReviewRequest,
    db: Session = Depends(get_db),
    current_user: userProfile = Depends(verify_access_token)
):
 
    customer = db.query(User).filter(
        User.id == current_user["user_id"]
    ).first()
 
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
 
    if customer.user_role != UserRole.CUSTOMER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Only customers can create reviews")
 
    if request.rating < 1 or request.rating > 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Rating must be between 1 and 5")
 

    food = db.query(Food).filter(Food.id == request.food_id).first()
 
    if not food:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Food not found")
 
    if food.resturent_id != request.restaurant_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Food does not belong to this restaurant")

    restaurant = db.query(Resturants).filter(Resturants.id == request.restaurant_id).first()
 
    if not restaurant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Restaurant not found")
 
    
    delivered_order_item = (
        db.query(Order_Item).join(Order).filter(Order.customer_id == customer.id,
                                                # Order.status == OrderStatus.DELIVERED,
                                                Order.restaurant_id == food.resturent_id,                   
                                                Order_Item.food_id == food.id).first())
 
    if not delivered_order_item:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="You can review only food that you have ordered")
 
    existing_review = db.query(Review).filter(Review.customer_id == customer.id,
                                              Review.restaurant_id == restaurant.id,
                                              Review.food_id == food.id).first()
 
    if existing_review:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="You have already reviewed this food")
 

    review = Review(customer_id=customer.id,restaurant_id=restaurant.id,food_id=food.id,rating=request.rating,comment=request.comment)
 
    db.add(review)
    db.commit()
    db.refresh(review)
 
    return {
        "message": "Food review created successfully",
 
        "review": {
            "id": review.id,
            "customer_id": review.customer_id,
            "restaurant_id": review.restaurant_id,
            "food_id": review.food_id,
            "rating": review.rating,
            "comment": review.comment,
            "created_at": review.created_at
        }
    }

@router.get("/restaurants/{restaurant_id}/reviews")
def get_restaurant_reviews(
    restaurant_id: int,
    db: Session = Depends(get_db)
):
 
 
    restaurant = db.query(Resturants).filter(Resturants.id == restaurant_id).first()
 
    if not restaurant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Restaurant not found")
 
    reviews = db.query(Review).filter(Review.restaurant_id == restaurant_id,
                                      Review.food_id.is_(None)).order_by(Review.created_at.desc()).all()
 
    average_rating = db.query(func.avg(Review.rating)).filter(Review.restaurant_id == restaurant_id,
                                                              Review.food_id.is_(None)).scalar()
 
 
    review_data = []
 
    for review in reviews:
 
        customer = db.query(User).filter(User.id == review.customer_id).first()
 
        review_data.append({
            "review_id": review.id,
            "customer_id": review.customer_id,
            "customer_name": customer.name if customer else None,
            "rating": review.rating,
            "comment": review.comment,
            "created_at": review.created_at,
            "updated_at": review.updated_at
        })
            
    return {
        "restaurant_id": restaurant_id,
        "restaurant_name": restaurant.resturant_name,
        "average_rating": round(float(average_rating), 2) if average_rating is not None else 0,
        "total_reviews": len(review_data),
        "reviews": review_data
    }
    
    
@router.get("/foods/{food_id}/reviews")
def get_food_reviews(food_id: int,db: Session = Depends(get_db)):
 
    food = db.query(Food).filter(Food.id == food_id).first()
 
    if not food:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Food not found")
 
    reviews = db.query(Review).filter(Review.food_id == food_id).order_by(Review.created_at.desc()).all()
 

    average_rating = db.query(func.avg(Review.rating)).filter(Review.food_id == food_id).scalar()
 
    review_data = []
 
    for review in reviews:
 
        customer = db.query(User).filter(User.id == review.customer_id).first()
 
        review_data.append({
            "review_id": review.id,
            "customer_id": review.customer_id,
            "customer_name": customer.name if customer else None,
            "rating": review.rating,
            "comment": review.comment,
            "created_at": review.created_at
        })
 

    return {
        "food_id": food.id,
        "food_name": food.food_name,
        "restaurant_id": food.resturent_id,
        "average_rating": round(float(average_rating), 2) if average_rating is not None else 0,
        "total_reviews": len(review_data),
        "reviews": review_data
    }
    

@router.put("/reviews/{review_id}")
def update_review(review_id: int,request: ReviewUpdateRequest,db: Session = Depends(get_db),current_user: userProfile = Depends(verify_access_token)):
 
    customer = db.query(User).filter(User.id == current_user["user_id"]).first()
 
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Customer not found")
 
    if customer.user_role != UserRole.CUSTOMER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Only customers can update reviews")
 
    review = db.query(Review).filter(Review.id == review_id,Review.customer_id == customer.id).first()
 
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Review not found")
 
    if request.rating is not None:
 
        if request.rating < 1 or request.rating > 5:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Rating must be between 1 and 5")
 
        review.rating = request.rating
  
    if request.comment is not None:
        review.comment = request.comment
 
    db.commit()
    db.refresh(review)
 
 
    return {
        "message": "Review updated successfully",
 
        "review": {
            "id": review.id,
            "customer_id": review.customer_id,
            "restaurant_id": review.restaurant_id,
            "food_id": review.food_id,
            "rating": review.rating,
            "comment": review.comment,
            "updated_at": review.updated_at
        }
    }

@router.delete("/reviews/{review_id}")
def delete_review(review_id: int,db: Session = Depends(get_db),current_user: userProfile = Depends(verify_access_token)):
 
    customer = db.query(User).filter(User.id == current_user["user_id"]).first()
 
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Customer not found")
 
    if customer.user_role != UserRole.CUSTOMER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Only customers can delete reviews")
 
 
    review = db.query(Review).filter(Review.id == review_id,Review.customer_id == customer.id).first()
 
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Review not found")
  
    db.delete(review)
    db.commit()
 
    return {
        "message": "Review deleted successfully",
        "review_id": review_id
    }