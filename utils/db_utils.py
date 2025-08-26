from sqlalchemy.orm import Session
from models.database_models import Query, Feedback, Conversation, Message
from datetime import datetime
import json

# FILE: utils/db_utils.py
from models.database_models import ChatSession, ChatMessage  # adjust based on your actual model location
from sqlalchemy.orm import Session
from sqlalchemy import desc
import uuid
import json



def log_query(db: Session, user_id: str, question: str, response: str, documents_used: list = None, response_time: float = None):
    """Log a query and its response to the database."""
    query = Query(
        user_id=user_id,
        question=question,
        response=response,
        documents_used=json.dumps(documents_used) if documents_used else None,
        response_time=response_time,
        created_at=datetime.utcnow()
    )
    db.add(query)
    db.commit()
    db.refresh(query)
    return query


def log_feedback(db: Session, user_id: str, query_id: int, rating: int, is_helpful: bool, feedback_text: str = None):
    """Log user feedback for a query."""
    feedback = Feedback(
        user_id=user_id,
        query_id=query_id,
        rating=rating,
        is_helpful=is_helpful,
        feedback_text=feedback_text,
        created_at=datetime.utcnow()
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return feedback


def get_user_queries(db: Session, user_id: str, limit: int = 10):
    """Get recent queries for a user."""
    return db.query(Query).filter(Query.user_id == user_id).order_by(Query.created_at.desc()).limit(limit).all()


def get_query_feedback(db: Session, query_id: int):
    """Get feedback for a specific query."""
    return db.query(Feedback).filter(Feedback.query_id == query_id).first()


def create_conversation(db: Session, user_id: str, title: str = "New Conversation"):
    conversation = Conversation(user_id=user_id, title=title)
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation


def get_user_conversations(db: Session, user_id: str, limit: int = 20):
    return db.query(Conversation).filter(Conversation.user_id == user_id).order_by(Conversation.updated_at.desc()).limit(limit).all()


def get_conversation(db: Session, conversation_id: int):
    return db.query(Conversation).filter(Conversation.id == conversation_id).first()


def update_conversation_title(db: Session, conversation_id: int, new_title: str):
    conversation = get_conversation(db, conversation_id)
    if conversation:
        conversation.title = new_title
        db.commit()
        db.refresh(conversation)
    return conversation


def delete_conversation(db: Session, conversation_id: int):
    conversation = get_conversation(db, conversation_id)
    if conversation:
        db.delete(conversation)
        db.commit()
    return conversation


def add_message(db: Session, conversation_id: int, role: str, content: str):
    message = Message(conversation_id=conversation_id,
                      role=role, content=content)
    db.add(message)
    db.commit()
    db.refresh(message)
    # Update conversation's updated_at
    conversation = get_conversation(db, conversation_id)
    if conversation:
        conversation.updated_at = message.timestamp
        db.commit()
    return message


def get_or_create_chat_session(db: Session, user_id: str, session_id: str):
    chat = db.query(ChatSession).filter_by(session_id=session_id, user_id=user_id).first()
    if not chat:
        chat = ChatSession(
            session_id=session_id,
            user_id=user_id,
            title=f"Chat {session_id[-5:]}"
        )
        db.add(chat)
        db.commit()
        db.refresh(chat)
    return chat

def save_chat_message(db: Session, chat_id: int, role: str, content: str, references: dict = None):
    msg = ChatMessage(
        chat_session_id=chat_id,
        role=role,
        content=content,
        references=json.dumps(references) if references else None
    )
    db.add(msg)
    db.commit()

def load_chat_history(db: Session, chat_id: int):
    messages = db.query(ChatMessage).filter_by(chat_session_id=chat_id).order_by(ChatMessage.created_at).all()
    history = []
    for msg in messages:
        history.append({
            "role": msg.role,
            "content": msg.content,
            "references": json.loads(msg.references) if msg.references else {}
        })
    return history

def get_user_chat_sessions(db: Session, user_id: str):
    sessions = db.query(ChatSession).filter_by(user_id=user_id).order_by(desc(ChatSession.created_at)).all()
    return [{
        "session_id": s.session_id,
        "title": s.title,
        "created_at": s.created_at
    } for s in sessions]

def delete_chat_session(db: Session, session_id: str, user_id: str):
    db.query(ChatMessage).filter(ChatMessage.chat_session_id == 
        db.query(ChatSession.id).filter_by(session_id=session_id, user_id=user_id).scalar()
    ).delete()
    db.query(ChatSession).filter_by(session_id=session_id, user_id=user_id).delete()
    db.commit()
