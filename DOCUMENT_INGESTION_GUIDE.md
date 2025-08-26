# 📚 Document Ingestion System Guide

## Overview

The document ingestion system is the core component that allows JuristAI to learn from legal documents and provide accurate, referenced responses. This system replaces the functionality of your previous `legal_pdf.py` file with a more robust, scalable solution.

## 🏗️ System Architecture

### **Backend Components**

1. **Document Service** (`backend/services/document_service.py`)
   - Handles PDF processing and text extraction
   - Manages document chunking and embedding generation
   - Extracts legal references automatically
   - Integrates with vector database

2. **Document Models** (`backend/models/document.py`)
   - `LegalDocument`: Stores document metadata and content
   - `DocumentChunk`: Stores processed chunks with embeddings
   - Supports country-specific filtering

3. **API Routes** (`backend/api/routes/documents.py`)
   - `/api/documents/upload` - Upload and process documents
   - `/api/documents/list` - List user documents
   - `/api/documents/{id}` - Get document details
   - `/api/documents/{id}` (DELETE) - Delete documents

### **Frontend Components**

1. **Document Upload** (`components/documents/DocumentUpload.tsx`)
   - Drag-and-drop file upload interface
   - Real-time upload progress
   - Document management and deletion

2. **Document Management Page** (`app/documents/page.tsx`)
   - Complete document management interface
   - Upload instructions and best practices

## 🔄 Document Processing Pipeline

### **Step 1: File Upload**
```
User uploads PDF → Frontend validation → Backend processing
```

**Validation:**
- File type: PDF only
- File size: Max 50MB
- User authentication required

### **Step 2: Text Extraction**
```python
# Using PyMuPDF with OCR fallback
def extract_text_from_pdf(file_path):
    doc = fitz.open(file_path)
    text_content = ""
    
    for page in doc:
        # Try direct text extraction first
        text = page.get_text()
        
        # If no text, use OCR
        if not text.strip():
            text = extract_text_with_ocr(page)
        
        text_content += text
    
    return text_content
```

### **Step 3: Document Chunking**
```python
def chunk_text(text, document_id):
    # Clean and normalize text
    text = clean_text(text)
    
    # Split into sentences (preserving legal citations)
    sentences = split_into_sentences(text)
    
    # Create overlapping chunks (1000 chars with 200 char overlap)
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        if len(current_chunk + sentence) > chunk_size:
            # Save current chunk
            chunks.append(create_chunk(current_chunk))
            # Start new chunk with overlap
            current_chunk = get_overlap_text(current_chunk) + sentence
        else:
            current_chunk += sentence
    
    return chunks
```

### **Step 4: Legal Reference Extraction**
```python
def extract_legal_references(text):
    references = {
        "laws": [],
        "cases": [],
        "articles": []
    }
    
    # Extract law references
    law_patterns = [
        r'Section\s+(\d+)\s+of\s+the\s+([A-Za-z\s]+(?:Act|Law|Code))',
        r'(\d+)\s+of\s+the\s+([A-Za-z\s]+(?:Act|Law|Code))'
    ]
    
    # Extract case references
    case_patterns = [
        r'([A-Za-z\s]+v\.\s+[A-Za-z\s]+)',
        r'case\s+of\s+([A-Za-z\s]+v\.\s+[A-Za-z\s]+)'
    ]
    
    # Extract article references
    article_patterns = [
        r'Article\s+(\d+)\s+of\s+the\s+([A-Za-z\s]+(?:Constitution|Charter))'
    ]
    
    return references
```

### **Step 5: Embedding Generation**
```python
def generate_embeddings(chunks):
    for chunk in chunks:
        # Generate embedding using OpenAI/Sentence Transformers
        embedding = get_embedding(chunk["content"])
        chunk["embedding"] = embedding
    return chunks
```

### **Step 6: Database Storage**
```python
def save_to_database(chunks, document_id):
    for chunk_data in chunks:
        chunk = DocumentChunk(
            id=chunk_data["id"],
            document_id=document_id,
            content=chunk_data["content"],
            embedding=chunk_data["embedding"],
            references=json.dumps(chunk_data["references"]),
            country=chunk_data["country"]
        )
        db.add(chunk)
    db.commit()
```

## 🗄️ Database Schema

### **Legal Documents Table**
```sql
CREATE TABLE legal_documents (
    id UUID PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    country VARCHAR(50) DEFAULT 'nigeria',
    document_type VARCHAR(100) DEFAULT 'legal_document',
    content TEXT NOT NULL,
    content_hash VARCHAR(32) UNIQUE NOT NULL,
    uploaded_at TIMESTAMP DEFAULT NOW(),
    status VARCHAR(20) DEFAULT 'processing'
);
```

### **Document Chunks Table**
```sql
CREATE TABLE document_chunks (
    id VARCHAR(255) PRIMARY KEY,
    document_id UUID REFERENCES legal_documents(id),
    content TEXT NOT NULL,
    chunk_number INTEGER NOT NULL,
    embedding VECTOR(1536) NOT NULL,
    references TEXT,
    country VARCHAR(50) DEFAULT 'nigeria',
    created_at TIMESTAMP DEFAULT NOW()
);
```

## 🔍 RAG Integration

### **Enhanced Context Retrieval**
```python
def get_context_from_db(query, country, k=4):
    # Generate query embedding
    query_embedding = get_embedding(query)
    
    # Search similar chunks with country filtering
    results = search_similar_chunks(
        query_embedding, 
        k=k, 
        country=country
    )
    
    return results
```

### **Reference Verification**
```python
def verify_reference_exists(reference, country):
    # Check if reference exists in database
    result = db.execute(
        "SELECT COUNT(*) FROM document_chunks WHERE references ILIKE %s AND country = %s",
        (f"%{reference}%", country)
    ).scalar()
    
    return result > 0
```

## 🚀 Usage Examples

### **Uploading Documents**
```bash
# Using the frontend interface
1. Navigate to /documents
2. Drag and drop PDF file
3. Select country jurisdiction
4. Click "Upload Document"
```

### **API Usage**
```bash
# Upload document via API
curl -X POST "http://localhost:8000/api/documents/upload" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@document.pdf" \
  -F "country=nigeria" \
  -F "document_type=legal_document"

# List documents
curl -X GET "http://localhost:8000/api/documents/list" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get document details
curl -X GET "http://localhost:8000/api/documents/{document_id}" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 🔧 Configuration

### **Environment Variables**
```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/jurist_ai

# AI Services
OPENAI_API_KEY=your_openai_key
GROQ_API_KEY=your_groq_key

# Document Processing
MAX_FILE_SIZE=52428800  # 50MB in bytes
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

### **Chunking Parameters**
```python
# Configurable chunking settings
CHUNK_SIZE = 1000  # characters per chunk
CHUNK_OVERLAP = 200  # characters overlap between chunks
MAX_CHUNKS_PER_DOCUMENT = 1000  # prevent excessive chunking
```

## 📊 Performance Optimizations

### **Batch Processing**
```python
# Process chunks in batches for better performance
async def process_chunks_batch(chunks, batch_size=10):
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        await process_batch(batch)
```

### **Caching**
```python
# Cache embeddings for frequently accessed chunks
@lru_cache(maxsize=1000)
def get_cached_embedding(text):
    return get_embedding(text)
```

### **Database Indexing**
```sql
-- Create indexes for better performance
CREATE INDEX idx_document_chunks_country ON document_chunks(country);
CREATE INDEX idx_document_chunks_embedding ON document_chunks USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX idx_legal_documents_user ON legal_documents(user_id);
```

## 🛡️ Security Features

### **File Validation**
- File type verification (PDF only)
- File size limits (50MB max)
- Content hash for deduplication
- User authentication required

### **Data Protection**
- User-specific document isolation
- Secure file handling with temporary files
- Input sanitization and validation
- SQL injection prevention

## 🔄 Migration from legal_pdf.py

### **Key Differences**

| Feature | legal_pdf.py | New System |
|---------|-------------|------------|
| **Architecture** | Monolithic | Microservices |
| **Database** | Basic storage | Vector database with pgvector |
| **Chunking** | Simple text split | Intelligent sentence-aware chunking |
| **References** | Manual extraction | Automated pattern matching |
| **Scalability** | Limited | Highly scalable |
| **User Management** | None | Multi-user support |
| **Country Support** | None | Multi-jurisdiction support |

### **Migration Steps**
1. **Install new dependencies**
   ```bash
   pip install PyMuPDF pytesseract Pillow pgvector
   ```

2. **Update database schema**
   ```sql
   -- Run the new table creation scripts
   -- Enable pgvector extension
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

3. **Migrate existing documents**
   ```python
   # Script to migrate existing PDFs to new system
   for pdf_file in existing_pdfs:
       process_document(pdf_file, user_id, country)
   ```

## 📈 Monitoring and Analytics

### **Document Statistics**
```python
# Get document statistics
stats = {
    "total_documents": 150,
    "total_chunks": 2500,
    "by_country": {
        "nigeria": 100,
        "ghana": 30,
        "kenya": 20
    },
    "by_type": {
        "legal_document": 120,
        "court_judgment": 20,
        "regulation": 10
    }
}
```

### **Processing Metrics**
- Upload success rate
- Processing time per document
- Chunk generation efficiency
- Reference extraction accuracy

## 🚀 Future Enhancements

### **Planned Features**
1. **Advanced OCR**: Better text extraction from scanned documents
2. **Document Versioning**: Track document updates and changes
3. **Collaborative Uploads**: Allow multiple users to contribute documents
4. **Document Categories**: Automatic categorization of legal documents
5. **Citation Network**: Build relationships between legal references

### **Performance Improvements**
1. **Parallel Processing**: Process multiple documents simultaneously
2. **Streaming Uploads**: Handle large files without memory issues
3. **Incremental Updates**: Update only changed parts of documents
4. **Smart Caching**: Cache frequently accessed chunks and embeddings

## 📞 Support

For questions about the document ingestion system:

- **Documentation**: This guide and inline code comments
- **API Reference**: `/docs` endpoint for interactive API documentation
- **Error Logs**: Check backend logs for processing errors
- **Performance**: Monitor database and embedding generation metrics

---

**JuristAI Document Ingestion System**
*Empowering legal AI with comprehensive knowledge management*
