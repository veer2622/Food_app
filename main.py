from fastapi import FastAPI
from api.router import *
# from food_project.models import usermodel
from core.database import Base,engine ,get_db
from fastapi.staticfiles import StaticFiles


app = FastAPI()
Base.metadata.create_all(engine)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.include_router(userRouter)
app.include_router(resturentRouter)
app.include_router(food_Router)
app.include_router(Cart_Router)
app.include_router(Address_Router)
app.include_router(Order_Router)
app.include_router(Payment_Router)
app.include_router(Review_Router)