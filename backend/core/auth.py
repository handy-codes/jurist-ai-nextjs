from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import os

# For now, we'll create a simple user model and auth
# In production, you'd want to integrate with Clerk properly

class User:
    def __init__(self, id: str, email: str = None):
        self.id = id
        self.email = email

# Simple bearer token security
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Get current user from token"""
    try:
        # For now, we'll accept any valid token
        # In production, you'd verify the token with Clerk
        token = credentials.credentials
        
        # Simple validation - you can enhance this later
        if not token or len(token) < 10:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # For now, we'll use a simple user ID from the token
        # In production, you'd decode the JWT and get user info from Clerk
        user_id = f"user_{hash(token) % 1000000}"
        
        return User(id=user_id)
        
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

# Optional: Create a function that doesn't require auth for testing
async def get_optional_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[User]:
    """Get current user if authenticated, otherwise return None"""
    try:
        if credentials:
            return await get_current_user(credentials)
    except:
        pass
    return None
