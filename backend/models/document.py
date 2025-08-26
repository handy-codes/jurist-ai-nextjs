from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, VECTOR
from datetime import datetime
import uuid

from core.database import Base

class LegalDocument(Base):
    __tablename__ = "legal_documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(String(255), nullable=False)
    user_id = Column(String(255), nullable=False)
    country = Column(String(50), nullable=False, default="nigeria")
    document_type = Column(String(100), nullable=False, default="legal_document")
    content = Column(Text, nullable=False)
    content_hash = Column(String(32), unique=True, nullable=False)  # MD5 hash for deduplication
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20), default="processing")  # processing, processed, error
    
    # Relationship to chunks
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")

class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    
    id = Column(String(255), primary_key=True)
    document_id = Column(UUID(as_uuid=True), ForeignKey("legal_documents.id"), nullable=False)
    content = Column(Text, nullable=False)
    chunk_number = Column(Integer, nullable=False)
    embedding = Column(VECTOR(1536), nullable=False)  # Using OpenAI embedding dimensions
    references = Column(Text)  # JSON string of legal references
    country = Column(String(50), nullable=False, default="nigeria")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to document
    document = relationship("LegalDocument", back_populates="chunks")
