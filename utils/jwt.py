from jose import jwt , JWTError
from passlib.context import CryptContext
from datetime import datetime, timezone, timedelta
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi import Depends,HTTPException, status

SECRET_KEY="MY5145SEC5KYE"
ALGORITHM= "HS256"
EXPIRE_TIME_IN_MINUTES = 30

security=HTTPBearer()
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

class Hash():
    
    def hashing(password):
        return pwd_context.hash(password)
    
    def verify(plain_password, hashed_password):
        return pwd_context.verify(plain_password,hashed_password)
    

def create_access_token(data:dict, expire_delta:timedelta | None=None):
    payload = data.copy()
    if expire_delta:
        expire = datetime.now(timezone.utc) + expire_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=EXPIRE_TIME_IN_MINUTES)
    payload.update({"exp":expire})
    token = jwt.encode(payload,SECRET_KEY,algorithm=ALGORITHM)
    return token

def verify_access_token(credential:HTTPAuthorizationCredentials=Depends(security)):
    token = credential.credentials
    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        
        username = payload.get("sub")
        user_id = payload.get("user_id")
        
        if not username:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")
        
        return {"username":username, "user_id":user_id}
     
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token Faield")    

