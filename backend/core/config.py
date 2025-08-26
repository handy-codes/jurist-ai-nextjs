from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    
    # AI Services
    GROQ_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    
    # Clerk Authentication
    CLERK_JWT_PUBLIC_KEY: Optional[str] = None
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # Redis
    REDIS_URL: Optional[str] = "redis://localhost:6379"
    
    class Config:
        env_file = ".env"

settings = Settings()
