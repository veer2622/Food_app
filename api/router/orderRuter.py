# import os, random, shutil, json
from fastapi import APIRouter,Depends,HTTPException,status
from core.database import get_db
# from core.redis import save_otp, verify_otp, redis_client
from sqlalchemy.orm import Session
from schemas import *
from models import *
from core.get_current_user import get_current_customer
from utils.jwt import verify_access_token
# from typing import List
# from sqlalchemy import func
from decimal import Decimal

router = APIRouter(tags= ["Order"])


@router.post("/Checkout")
def checkout(request:CheckoutRequest, db:Session=Depends(get_db), current_user:userProfile=Depends(verify_access_token)):
    try:
        customer = get_current_customer(db,current_user)
        
        cart = db.query(Cart).filter(Cart.id == request.cart_id, Cart.customer_id == customer.id).first()
        if not cart:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart Not Found")
        
        cart_items = db.query(Cart_Item).filter(Cart_Item.cart_id == cart.id, Cart_Item.is_deleted == False).all()
        if not cart_items:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart is empty")
        
        address = db.query(Address).filter(Address.id == request.address_id,Address.customer_id == customer.id).first()
        if not address:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Address not found")
        
        subtotal = Decimal("0.00")
        restaurant_id = None
        for cart_item in cart_items:

            food = db.query(Food).filter(Food.id == cart_item.food_id).first()
            if not food:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail=f"Food {cart_item.food_id} not found")
            
            if restaurant_id is None:
                restaurant_id = food.resturent_id

            elif restaurant_id != food.resturent_id:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Cart cannot contain food from different restaurants")
            
            if cart_item.quantity <= 0:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Invalid food quantity")        
            
            item_subtotal = (Decimal(str(food.food_price)) * cart_item.quantity)
            subtotal += item_subtotal
            
        delivery_fee = Decimal("40.00")        
        total_amount = subtotal + delivery_fee
        order = Order(
            customer_id=customer.id,
            restaurant_id=restaurant_id,
            address_id=address.id,
            status=OrderStatus.PENDING,
            payment_status=PaymentStatus.PENDING,
            subtotal=subtotal,
            delivery_fee=delivery_fee,
            total_amount=total_amount,
            delivery_name=address.name,
            delivery_number=address.number,
            delivery_address=address.address_line_1,
            # delivery_address_2=address.address_line_2,
            delivery_city=address.city,
            delivery_state=address.state,
            delivery_pincode=address.pincode
        )
        db.add(order)
        db.flush()

        for cart_item in cart_items:

            food = db.query(Food).filter(Food.id == cart_item.food_id).first()
            item_price = Decimal(str(food.food_price))
            item_subtotal = (item_price * cart_item.quantity)
            order_item = Order_Item(order_id=order.id,food_id=food.id,food_name=food.food_name,
                                    price=item_price,quantity=cart_item.quantity,subtotal=item_subtotal)
            db.add(order_item)
            
        cart.status = CartStatus.CHECKED_OUT
        
        for cart_item in cart_items:
            cart_item.is_deleted = True
        db.commit()
        db.refresh(order)
        
        return {
            "message": "Order created successfully",
            "order_id": order.id,
            "customer_id": order.customer_id,
            "restaurant_id": order.restaurant_id,

            "status": order.status,
            "payment_status": order.payment_status,

            "subtotal": order.subtotal,
            "delivery_fee": order.delivery_fee,
            "total_amount": order.total_amount,

            "delivery_address": {
                "name": order.delivery_name,
                "number": order.delivery_number,
                "address": order.delivery_address,
                "city": order.delivery_city,
                "state": order.delivery_state,
                "pincode": order.delivery_pincode
            }
        }
    
    except HTTPException:
        db.rollback()
        raise

    except Exception as e:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
        
# @router.post("/add-order")
# def add_order(request:Add_Order, db:Session=Depends(get_db), current_user:userProfile=Depends(verify_access_token)):

#     cart = (db.query(Cart).options(joinedload(Cart.cart_item).joinedload(Cart_Item.food)).filter(Cart.customer_id == current_user["user_id"]).first())
#     if not cart:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found")
#     if not Cart.cart_item:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cart is empty")
    
#     address = db.query(Address).filter(Address.id== request.address_id, Address.customer_id == current_user["user_id"]).first()
#     if not address:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address Not Available")
    
#     resturent = db.query(Resturants).filter(Resturants.id == request.resturant_id).first()
#     if not resturent:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="resturent Not Available")

#     sub_total = cart.total
#     total_amount_ = sub_total + request.delivery_fee
#     new_Order=Order(customer_id = current_user["user_id"],restaurant_id=request.resturant_id,address_id=request.address_id,
#                     subtotal=sub_total, total_amount=total_amount_,  delivery_fee=request.delivery_fee,
#                     delivery_name=request.delivery_name,delivery_number=request.delivery_number,delivery_address=request.delivery_address,
#                     delivery_city=request.delivery_city,delivery_state=request.delivery_state,delivery_pincode=request.delivery_pincode)
#     db.add(new_Order)
#     db.commit()
#     db.refresh(new_Order)
    
    # cart= db.query(Cart).filter(Cart.customer_id == new_Order.customer_id)
    # cart.delete(synchronize_session=False)
    # db.commit()
    # return new_Order
@router.get("/orders")
def get_orders(
    db: Session = Depends(get_db),
    current_user: userProfile = Depends(verify_access_token)
):

    customer = get_current_customer(db,current_user)

    orders = db.query(Order).filter(Order.customer_id == customer.id).order_by(Order.created_at.desc()).all()
    if not orders:
        return {"message": "No orders found","orders": []}

    result = []

    for order in orders:

        result.append({
            "order_id": order.id,
            "restaurant_id": order.restaurant_id,
            "status": order.status,
            "payment_status": order.payment_status,
            "subtotal": order.subtotal,
            "delivery_fee": order.delivery_fee,
            "total_amount": order.total_amount,
            "created_at": order.created_at
        })

    return {
        "message": "Orders fetched successfully",
        "total_orders": len(result),
        "orders": result
    }


@router.get("/orders/{order_id}")
def get_order(order_id: int,db: Session = Depends(get_db),current_user: userProfile = Depends(verify_access_token)):

    customer = get_current_customer(db,current_user)

    order = db.query(Order).filter(Order.id == order_id,Order.customer_id == customer.id).first()

    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Order not found")

    order_items = db.query(Order_Item).filter(Order_Item.order_id == order.id).all()

    items = []

    for item in order_items:

        items.append({
            "order_item_id": item.id,
            "food_id": item.food_id,
            "food_name": item.food_name,
            "price": item.price,
            "quantity": item.quantity,
            "subtotal": item.subtotal
        })

    payment = db.query(Payment).filter(Payment.order_id == order.id).first()

    payment_data = None

    if payment:

        payment_data = {
            "payment_id": payment.id,
            "payment_method": payment.payment_method,
            "status": payment.status,
            "amount": payment.amount,
            "transaction_id": payment.transaction_id,
            "created_at": payment.created_at
        }

    delivery_address = {
        "name": order.delivery_name,
        "number": order.delivery_number,
        "address": order.delivery_address,
        "city": order.delivery_city,
        "state": order.delivery_state,
        "pincode": order.delivery_pincode
    }

    return {
        "message": "Order fetched successfully",

        "order": {
            "order_id": order.id,
            "customer_id": order.customer_id,
            "restaurant_id": order.restaurant_id,

            "status": order.status,
            "payment_status": order.payment_status,

            "subtotal": order.subtotal,
            "delivery_fee": order.delivery_fee,
            "total_amount": order.total_amount,

            "created_at": order.created_at,

            "items": items,

            "delivery_address": delivery_address,

            "payment": payment_data
        }
    }