from pydantic import BaseModel

class login_responce(BaseModel):
    username:str
    password:str

class forgot_pass(BaseModel):
    email:str
class verify_user(BaseModel):
    email:str
    otp:str

class varify_otp(BaseModel):
    email:str
    otp:str

class reset_otp(BaseModel):
    email:str
    password:str
    confirm_password:str
