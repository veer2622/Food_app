from pydantic import BaseModel,Field, field_validator
from typing import Optional

class Add_Address(BaseModel):
    name:str
    number:str
    address_line_1:str
    address_line_2:str 
    city:str
    state:str
    pincode:str = Field(..., description="only take number")
    
    @field_validator("pincode")
    @classmethod
        
    def pincode_validator(cls, value:str) -> str:
        if len(value) != 6:
            raise ValueError("PinCode must me 6 digit")
        
        for char in value:
            if not char.isdigit():
                raise ValueError("Only numbber give as input")
            # if char.isalpha():
            #     raise ValueError("alfabet not allow ")
            
        return value
        
    class Config:
        from_attributes=True
            
class Update_Address(Add_Address):
    name:Optional[str] = None
    number:Optional[str] = None
    address_line_1:Optional[str] = None
    address_line_2:Optional[str] = None
    city:Optional[str] = None
    state:Optional[str] = None
    pincode:Optional[str]  = Field(default=None,description="only take number")
    
    @field_validator("pincode")
    @classmethod    
    def pincode_validator(cls, value: str | None) -> str | None:
        if value is None:
            return None

        if len(value) != 6:
            raise ValueError("Pincode must be 6 digits")

        if not value.isdigit():
            raise ValueError("Only numbers are allowed")

        return value

    
    class Config:
        from_attributes = True

class Delete_Address(BaseModel):
    id:int
    
    class Config:
        from_attributes = True