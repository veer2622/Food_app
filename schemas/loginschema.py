from pydantic import BaseModel

class login_responce(BaseModel):
    username:str
    password:str

class verify_user(BaseModel):
    email:str
    otp:str