from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import httpx
import os

from core.auth import get_current_user
from core.database import get_db
from services.chat_service import ChatService
from models.user import User

router = APIRouter()

class ChatMessage(BaseModel):
    content: str
    country: str = "nigeria"

class ChatResponse(BaseModel):
    id: str
    role: str
    content: str
    references: Optional[dict] = None
    timestamp: str

@router.post("/send", response_model=ChatResponse)
async def send_message(
    message: ChatMessage,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """Send a message to the AI chat assistant"""
    try:
        chat_service = ChatService(db)
        response = await chat_service.process_message(
            user_id=current_user.id,
            content=message.content,
            country=message.country
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history", response_model=List[ChatResponse])
async def get_chat_history(
    session_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get chat history for the current user"""
    try:
        chat_service = ChatService(db)
        history = await chat_service.get_chat_history(
            user_id=current_user.id,
            session_id=session_id
        )
        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions")
async def get_chat_sessions(
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get all chat sessions for the current user"""
    try:
        chat_service = ChatService(db)
        sessions = await chat_service.get_sessions(user_id=current_user.id)
        return sessions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sessions")
async def create_chat_session(
    title: str = "New Chat",
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """Create a new chat session"""
    try:
        chat_service = ChatService(db)
        session = await chat_service.create_session(
            user_id=current_user.id,
            title=title
        )
        return session
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
