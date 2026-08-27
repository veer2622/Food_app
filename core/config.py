from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DB_HOST:str
    DB_PORT:int
    DB_USER:str
    DB_NAME:str
    DB_PASSWORD:str
    
    SECRET_KEY:str
    ALGORITHM:str
    ACCESS_TOKEN_EXPIRE_MINUTES:int
    
    
    SMTP_SERVER :str
    SMTP_PORT : int
    SMTP_EMAIL :str
    SMTP_PASSWORD:str
    
    model_config=SettingsConfigDict(
        env_file=".env")

settings = Settings()
