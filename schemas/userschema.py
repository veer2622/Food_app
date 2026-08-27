from pydantic import BaseModel,Field, field_validator

class user(BaseModel):
    name:str
    number:str
    email:str
    password:str = Field(..., description="password must be 12 character Long and Contain minimum one digit and one Capitle word, 1 special word")
    
    @field_validator("password")
    @classmethod
    
    def password_validator(cls, value:str) -> str:
        if len(value)<11:
            raise ValueError("Password must me 12 degit Long")
        
        for char in value:
            if not any(char.isdigit):
                raise ValueError("take atleast one digit in ur password")
            
            if not any(char.isupper):
                raise ValueError("Take Atleast one Upper case")
            # if char.isdigit:
            #     raise ValueError("only take number")
            
            # if not any (char.is)
        
class userresponce(BaseModel):
    name:str
    number:str
    email:str
    class Config():
        from_attributes = True
    
class userProfile(BaseModel):
    name:str
    number:str
    email:str
    password:str
    profile_pic:str
    
    class Config():
        from_attributes = True

class delete_user(BaseModel):
    is_active: bool
