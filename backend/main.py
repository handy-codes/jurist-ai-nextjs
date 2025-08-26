from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

from api.routes import chat, documents, templates, search, feedback
from core.config import settings
from core.database import engine, Base
from models.user import User
from models.chat import ChatSession, ChatMessage

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown
    pass

app = FastAPI(
    title="JuristAI API",
    description="Nigerian Legal AI Assistant API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "https://jurist-ai.vercel.app",
        "https://jurist-ai-frontend.vercel.app",
        "https://jurist-ai-backend.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
app.include_router(templates.router, prefix="/api/templates", tags=["templates"])
app.include_router(search.router, prefix="/api/search", tags=["search"])
app.include_router(feedback.router, prefix="/api/feedback", tags=["feedback"])

@app.get("/")
async def root():
    return {"message": "JuristAI API - Nigerian Legal AI Assistant"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
