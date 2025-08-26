from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from config.database import Base
from pgvector.sqlalchemy import Vector


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True)  # Clerk user ID
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # Relationships
    queries = relationship("Query", back_populates="user")
    feedback = relationship("Feedback", back_populates="user")
    conversations = relationship("Conversation", back_populates="user")


class Query(Base):
    __tablename__ = "queries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    question = Column(Text)
    response = Column(Text)
    documents_used = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    response_time = Column(Float)

    user = relationship("User", back_populates="queries")
    feedback = relationship("Feedback", back_populates="query")


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    query_id = Column(Integer, ForeignKey("queries.id"))
    rating = Column(Integer)
    is_helpful = Column(Boolean)
    feedback_text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="feedback")
    query = relationship("Query", back_populates="feedback")


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    title = Column(String, default="New Conversation")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    role = Column(String)
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

    conversation = relationship("Conversation", back_populates="messages")


class LegalChunk(Base):
    __tablename__ = "legal_chunks"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    source = Column(String, nullable=True)
    embedding = Column(Vector(1536))  # Adjust this if using another dimension


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True)
    user_id = Column(String, index=True)
    title = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    messages = relationship("ChatMessage", back_populates="chat_session", cascade="all, delete")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    chat_session_id = Column(Integer, ForeignKey("chat_sessions.id"))
    role = Column(String)
    content = Column(Text)
    references = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    chat_session = relationship("ChatSession", back_populates="messages")



# from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, Boolean
# from sqlalchemy.orm import relationship
# from datetime import datetime
# from config.database import Base
# from pgvector.sqlalchemy import Vector

# # FILE: models.py

# from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
# from sqlalchemy.orm import relationship
# from sqlalchemy.sql import func
# from config.database import Base  # make sure config/database.py defines Base = declarative_base()



# class User(Base):
#     __tablename__ = "users"

#     id = Column(String, primary_key=True)  # Clerk user ID
#     email = Column(String, unique=True, index=True)
#     full_name = Column(String)
#     created_at = Column(DateTime, default=datetime.utcnow)
#     is_active = Column(Boolean, default=True)

#     # Relationships
#     queries = relationship("Query", back_populates="user")
#     feedback = relationship("Feedback", back_populates="user")


# class Query(Base):
#     __tablename__ = "queries"

#     id = Column(Integer, primary_key=True, index=True)
#     user_id = Column(String, ForeignKey("users.id"))
#     question = Column(Text)
#     response = Column(Text)
#     documents_used = Column(Text)  # JSON string of document references
#     created_at = Column(DateTime, default=datetime.utcnow)
#     response_time = Column(Float)  # in seconds

#     # Relationships
#     user = relationship("User", back_populates="queries")
#     feedback = relationship("Feedback", back_populates="query")


# class Feedback(Base):
#     __tablename__ = "feedback"

#     id = Column(Integer, primary_key=True, index=True)
#     user_id = Column(String, ForeignKey("users.id"))
#     query_id = Column(Integer, ForeignKey("queries.id"))
#     rating = Column(Integer)  # 1-5 stars
#     is_helpful = Column(Boolean)
#     feedback_text = Column(Text, nullable=True)
#     created_at = Column(DateTime, default=datetime.utcnow)

#     # Relationships
#     user = relationship("User", back_populates="feedback")
#     query = relationship("Query", back_populates="feedback")


# class Conversation(Base):
#     __tablename__ = "conversations"

#     id = Column(Integer, primary_key=True, index=True)
#     user_id = Column(String, ForeignKey("users.id"))
#     title = Column(String, default="New Conversation")
#     created_at = Column(DateTime, default=datetime.utcnow)
#     updated_at = Column(DateTime, default=datetime.utcnow,
#                         onupdate=datetime.utcnow)

#     # Relationships
#     user = relationship("User", backref="conversations")
#     messages = relationship(
#         "Message", back_populates="conversation", cascade="all, delete-orphan")


# class Message(Base):
#     __tablename__ = "messages"

#     id = Column(Integer, primary_key=True, index=True)
#     conversation_id = Column(Integer, ForeignKey("conversations.id"))
#     role = Column(String)  # 'user' or 'assistant'
#     content = Column(Text)
#     timestamp = Column(DateTime, default=datetime.utcnow)

#     # Relationships
#     conversation = relationship("Conversation", back_populates="messages")


# class LegalChunk(Base):
#     __tablename__ = "legal_chunks"

#     id = Column(Integer, primary_key=True, index=True)
#     text = Column(Text, nullable=False)
#     source = Column(String, nullable=True)
#     # Adjust dimension if your vectors use something else
#     embedding = Column(Vector(1536))

# class ChatSession(Base):
#     __tablename__ = "chat_sessions"

#     id = Column(Integer, primary_key=True, index=True)
#     session_id = Column(String, unique=True, index=True)
#     user_id = Column(String, index=True)
#     title = Column(String)
#     created_at = Column(DateTime(timezone=True), server_default=func.now())

#     messages = relationship("ChatMessage", back_populates="chat_session", cascade="all, delete")

# class ChatMessage(Base):
#     __tablename__ = "chat_messages"

#     id = Column(Integer, primary_key=True, index=True)
#     chat_session_id = Column(Integer, ForeignKey("chat_sessions.id"))
#     role = Column(String)
#     content = Column(Text)
#     references = Column(Text, nullable=True)
#     created_at = Column(DateTime(timezone=True), server_default=func.now())

#     chat_session = relationship("ChatSession", back_populates="messages")

