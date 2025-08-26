from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from typing import List, Optional
import os
import tempfile
import shutil

from core.auth import get_current_user
from core.database import get_db
from services.document_service import DocumentService
from models.user import User
from models.document import LegalDocument, DocumentChunk

router = APIRouter()

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    country: str = Form("nigeria"),
    document_type: str = Form("legal_document"),
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """Upload and process a legal document"""
    
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    # Validate file size (max 50MB)
    if file.size and file.size > 50 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size must be less than 50MB")
    
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            temp_file_path = temp_file.name
        
        # Process document
        document_service = DocumentService(db)
        result = await document_service.process_document(
            file_path=temp_file_path,
            filename=file.filename,
            user_id=current_user.id,
            country=country,
            document_type=document_type
        )
        
        # Clean up temporary file
        os.unlink(temp_file_path)
        
        if result["success"]:
            return JSONResponse(
                status_code=200,
                content={
                    "message": "Document uploaded and processed successfully",
                    "document_id": result["document_id"],
                    "filename": result["filename"],
                    "chunks_processed": result["chunks_processed"],
                    "country": result["country"]
                }
            )
        else:
            raise HTTPException(status_code=500, detail=result["error"])
            
    except Exception as e:
        # Clean up temporary file if it exists
        if 'temp_file_path' in locals():
            try:
                os.unlink(temp_file_path)
            except:
                pass
        
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

@router.get("/list")
async def list_documents(
    country: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """List all documents for the current user"""
    
    try:
        document_service = DocumentService(db)
        
        if country:
            documents = await document_service.get_documents_by_country(country)
        else:
            # Get all documents for user
            documents = db.query(LegalDocument).filter(
                LegalDocument.user_id == current_user.id
            ).all()
            
            documents = [
                {
                    "id": doc.id,
                    "filename": doc.filename,
                    "document_type": doc.document_type,
                    "country": doc.country,
                    "uploaded_at": doc.uploaded_at.isoformat(),
                    "status": doc.status
                }
                for doc in documents
            ]
        
        return {
            "documents": documents,
            "total": len(documents)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving documents: {str(e)}")

@router.get("/{document_id}")
async def get_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get document details and chunks"""
    
    try:
        document = db.query(LegalDocument).filter(
            LegalDocument.id == document_id,
            LegalDocument.user_id == current_user.id
        ).first()
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Get chunks for this document
        chunks = db.query(DocumentChunk).filter(
            DocumentChunk.document_id == document_id
        ).order_by(DocumentChunk.chunk_number).all()
        
        return {
            "document": {
                "id": document.id,
                "filename": document.filename,
                "document_type": document.document_type,
                "country": document.country,
                "uploaded_at": document.uploaded_at.isoformat(),
                "status": document.status,
                "content_length": len(document.content)
            },
            "chunks": [
                {
                    "id": chunk.id,
                    "chunk_number": chunk.chunk_number,
                    "content_preview": chunk.content[:200] + "..." if len(chunk.content) > 200 else chunk.content,
                    "references": eval(chunk.references) if chunk.references else {},
                    "created_at": chunk.created_at.isoformat()
                }
                for chunk in chunks
            ],
            "total_chunks": len(chunks)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving document: {str(e)}")

@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """Delete a document and all its chunks"""
    
    try:
        # Verify document belongs to user
        document = db.query(LegalDocument).filter(
            LegalDocument.id == document_id,
            LegalDocument.user_id == current_user.id
        ).first()
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Delete document and chunks
        document_service = DocumentService(db)
        success = await document_service.delete_document(document_id)
        
        if success:
            return {"message": "Document deleted successfully"}
        else:
            raise HTTPException(status_code=500, detail="Error deleting document")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting document: {str(e)}")

@router.get("/countries/{country}/documents")
async def get_documents_by_country(
    country: str,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get all documents for a specific country"""
    
    try:
        document_service = DocumentService(db)
        documents = await document_service.get_documents_by_country(country)
        
        return {
            "country": country,
            "documents": documents,
            "total": len(documents)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving documents: {str(e)}")

@router.get("/stats/overview")
async def get_document_stats(
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get document statistics for the user"""
    
    try:
        # Get total documents
        total_documents = db.query(LegalDocument).filter(
            LegalDocument.user_id == current_user.id
        ).count()
        
        # Get documents by country
        country_stats = db.query(
            LegalDocument.country,
            db.func.count(LegalDocument.id).label('count')
        ).filter(
            LegalDocument.user_id == current_user.id
        ).group_by(LegalDocument.country).all()
        
        # Get documents by type
        type_stats = db.query(
            LegalDocument.document_type,
            db.func.count(LegalDocument.id).label('count')
        ).filter(
            LegalDocument.user_id == current_user.id
        ).group_by(LegalDocument.document_type).all()
        
        # Get total chunks
        total_chunks = db.query(DocumentChunk).join(LegalDocument).filter(
            LegalDocument.user_id == current_user.id
        ).count()
        
        return {
            "total_documents": total_documents,
            "total_chunks": total_chunks,
            "by_country": {stat.country: stat.count for stat in country_stats},
            "by_type": {stat.document_type: stat.count for stat in type_stats}
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving statistics: {str(e)}")
