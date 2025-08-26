import os
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
import re
from typing import List, Dict, Optional
from datetime import datetime
import uuid
import hashlib

from utils.embedding import get_embedding
from utils.vector_db import add_chunk_to_db
from models.document import LegalDocument, DocumentChunk
from core.database import get_db

class DocumentService:
    def __init__(self, db):
        self.db = db
        self.chunk_size = 1000
        self.chunk_overlap = 200

    async def process_document(
        self, 
        file_path: str, 
        filename: str, 
        user_id: str, 
        country: str = "nigeria",
        document_type: str = "legal_document"
    ) -> Dict:
        """Process uploaded document and add to knowledge base"""
        
        try:
            # Extract text from PDF
            text_content = await self._extract_text_from_pdf(file_path)
            
            if not text_content.strip():
                raise ValueError("No text content extracted from document")
            
            # Create document record
            document = await self._create_document_record(
                filename, user_id, country, document_type, text_content
            )
            
            # Chunk the text
            chunks = await self._chunk_text(text_content, document.id)
            
            # Process chunks and add to vector database
            processed_chunks = await self._process_chunks(chunks, country)
            
            # Save chunks to database
            await self._save_chunks_to_db(processed_chunks, document.id)
            
            return {
                "success": True,
                "document_id": document.id,
                "filename": filename,
                "chunks_processed": len(processed_chunks),
                "country": country,
                "document_type": document_type
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    async def _extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF using PyMuPDF with OCR fallback"""
        try:
            doc = fitz.open(file_path)
            text_content = ""
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                
                # Try to extract text directly
                text = page.get_text()
                
                # If no text found, try OCR
                if not text.strip():
                    text = await self._extract_text_with_ocr(page)
                
                text_content += f"\n\n--- Page {page_num + 1} ---\n\n{text}"
            
            doc.close()
            return text_content
            
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")

    async def _extract_text_with_ocr(self, page) -> str:
        """Extract text using OCR for scanned pages"""
        try:
            # Convert page to image
            pix = page.get_pixmap()
            img_data = pix.tobytes("png")
            img = Image.open(io.BytesIO(img_data))
            
            # Use OCR to extract text
            text = pytesseract.image_to_string(img)
            return text
            
        except Exception as e:
            print(f"OCR extraction failed: {e}")
            return ""

    async def _create_document_record(
        self, 
        filename: str, 
        user_id: str, 
        country: str, 
        document_type: str, 
        content: str
    ) -> LegalDocument:
        """Create document record in database"""
        
        # Generate document hash for deduplication
        content_hash = hashlib.md5(content.encode()).hexdigest()
        
        document = LegalDocument(
            id=str(uuid.uuid4()),
            filename=filename,
            user_id=user_id,
            country=country,
            document_type=document_type,
            content=content,
            content_hash=content_hash,
            uploaded_at=datetime.utcnow(),
            status="processed"
        )
        
        self.db.add(document)
        self.db.commit()
        
        return document

    async def _chunk_text(self, text: str, document_id: str) -> List[Dict]:
        """Split text into overlapping chunks"""
        chunks = []
        
        # Clean and normalize text
        text = self._clean_text(text)
        
        # Split into sentences first
        sentences = self._split_into_sentences(text)
        
        current_chunk = ""
        chunk_id = 1
        
        for sentence in sentences:
            # If adding this sentence would exceed chunk size
            if len(current_chunk + sentence) > self.chunk_size and current_chunk:
                # Save current chunk
                chunks.append({
                    "id": f"{document_id}_chunk_{chunk_id}",
                    "content": current_chunk.strip(),
                    "chunk_number": chunk_id,
                    "document_id": document_id
                })
                
                # Start new chunk with overlap
                overlap_text = self._get_overlap_text(current_chunk)
                current_chunk = overlap_text + sentence
                chunk_id += 1
            else:
                current_chunk += sentence + " "
        
        # Add final chunk
        if current_chunk.strip():
            chunks.append({
                "id": f"{document_id}_chunk_{chunk_id}",
                "content": current_chunk.strip(),
                "chunk_number": chunk_id,
                "document_id": document_id
            })
        
        return chunks

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove page markers
        text = re.sub(r'--- Page \d+ ---', '', text)
        
        # Remove headers/footers (common patterns)
        text = re.sub(r'^\d+\s*$', '', text, flags=re.MULTILINE)
        
        return text.strip()

    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences while preserving legal citations"""
        # Split on sentence endings, but be careful with legal citations
        sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)
        
        # Handle legal citations that might be split incorrectly
        processed_sentences = []
        for sentence in sentences:
            # If sentence contains legal citation patterns, don't split further
            if re.search(r'(Section|Sections?|Article|Articles?)\s+\d+', sentence):
                processed_sentences.append(sentence)
            else:
                processed_sentences.append(sentence)
        
        return processed_sentences

    def _get_overlap_text(self, text: str) -> str:
        """Get overlap text from end of chunk"""
        words = text.split()
        if len(words) <= self.chunk_overlap // 10:  # Approximate word count
            return text
        
        overlap_words = words[-(self.chunk_overlap // 10):]
        return " ".join(overlap_words) + " "

    async def _process_chunks(self, chunks: List[Dict], country: str) -> List[Dict]:
        """Process chunks and generate embeddings"""
        processed_chunks = []
        
        for chunk in chunks:
            try:
                # Generate embedding for chunk
                embedding = await get_embedding(chunk["content"])
                
                # Extract legal references from chunk
                references = await self._extract_legal_references(chunk["content"])
                
                processed_chunk = {
                    **chunk,
                    "embedding": embedding,
                    "references": references,
                    "country": country,
                    "created_at": datetime.utcnow()
                }
                
                processed_chunks.append(processed_chunk)
                
            except Exception as e:
                print(f"Error processing chunk {chunk['id']}: {e}")
                continue
        
        return processed_chunks

    async def _extract_legal_references(self, text: str) -> Dict:
        """Extract legal references from text chunk"""
        references = {
            "laws": [],
            "cases": [],
            "articles": []
        }
        
        # Extract law references
        law_patterns = [
            r'Section\s+(\d+(?:-\d+)?(?:\s+and\s+\d+)?)\s+of\s+the\s+([A-Za-z\s]+(?:Act|Law|Code|Regulation))',
            r'(\d+(?:-\d+)?(?:\s+and\s+\d+)?)\s+of\s+the\s+([A-Za-z\s]+(?:Act|Law|Code|Regulation))',
            r'([A-Za-z\s]+(?:Act|Law|Code|Regulation))\s+Section\s+(\d+(?:-\d+)?(?:\s+and\s+\d+)?)'
        ]
        
        for pattern in law_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if len(match) == 2:
                    references["laws"].append(f"Section {match[0]} of the {match[1]}")
        
        # Extract case references
        case_patterns = [
            r'([A-Za-z\s]+v\.\s+[A-Za-z\s]+)',
            r'case\s+of\s+([A-Za-z\s]+v\.\s+[A-Za-z\s]+)',
            r'([A-Za-z\s]+)\s+v\.\s+([A-Za-z\s]+)'
        ]
        
        for pattern in case_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    references["cases"].append(f"{match[0]} v. {match[1]}")
                else:
                    references["cases"].append(match)
        
        # Extract article references
        article_patterns = [
            r'Article\s+(\d+(?:-\d+)?(?:\s+and\s+\d+)?)\s+of\s+the\s+([A-Za-z\s]+(?:Constitution|Charter|Treaty))',
            r'(\d+(?:-\d+)?(?:\s+and\s+\d+)?)\s+of\s+the\s+([A-Za-z\s]+(?:Constitution|Charter|Treaty))'
        ]
        
        for pattern in article_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if len(match) == 2:
                    references["articles"].append(f"Article {match[0]} of the {match[1]}")
        
        # Remove duplicates
        for key in references:
            references[key] = list(set(references[key]))
        
        return references

    async def _save_chunks_to_db(self, chunks: List[Dict], document_id: str):
        """Save processed chunks to database"""
        for chunk_data in chunks:
            chunk = DocumentChunk(
                id=chunk_data["id"],
                document_id=document_id,
                content=chunk_data["content"],
                chunk_number=chunk_data["chunk_number"],
                embedding=chunk_data["embedding"],
                references=str(chunk_data["references"]),
                country=chunk_data["country"],
                created_at=chunk_data["created_at"]
            )
            
            self.db.add(chunk)
        
        self.db.commit()

    async def get_documents_by_country(self, country: str) -> List[Dict]:
        """Get all documents for a specific country"""
        documents = self.db.query(LegalDocument).filter(
            LegalDocument.country == country
        ).all()
        
        return [
            {
                "id": doc.id,
                "filename": doc.filename,
                "document_type": doc.document_type,
                "uploaded_at": doc.uploaded_at.isoformat(),
                "status": doc.status
            }
            for doc in documents
        ]

    async def delete_document(self, document_id: str) -> bool:
        """Delete document and all its chunks"""
        try:
            # Delete chunks first
            self.db.query(DocumentChunk).filter(
                DocumentChunk.document_id == document_id
            ).delete()
            
            # Delete document
            self.db.query(LegalDocument).filter(
                LegalDocument.id == document_id
            ).delete()
            
            self.db.commit()
            return True
            
        except Exception as e:
            print(f"Error deleting document: {e}")
            return False
