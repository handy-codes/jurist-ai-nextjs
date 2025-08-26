import { NextRequest, NextResponse } from 'next/server'
import { auth } from '@clerk/nextjs'
import { writeFile, mkdir } from 'fs/promises'
import { join } from 'path'
import { existsSync } from 'fs'

const ALLOWED_FILE_TYPES = [
  'application/pdf',
  'application/msword',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  'application/vnd.ms-excel',
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
  'text/plain',
  'application/rtf'
]

const MAX_FILE_SIZE = 10 * 1024 * 1024 // 10MB
const MAX_UPLOADS_PER_DAY = 5

// Simple in-memory storage for upload tracking (in production, use Redis or database)
const uploadCounts = new Map<string, { count: number; date: string }>()

export async function POST(request: NextRequest) {
  try {
    const { userId } = await auth()
    
    if (!userId) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    // Check daily upload limit
    const today = new Date().toDateString()
    const userKey = `${userId}-${today}`
    const userUploads = uploadCounts.get(userKey) || { count: 0, date: today }
    
    if (userUploads.date !== today) {
      userUploads.count = 0
      userUploads.date = today
    }
    
    if (userUploads.count >= MAX_UPLOADS_PER_DAY) {
      return NextResponse.json(
        { error: `Daily upload limit of ${MAX_UPLOADS_PER_DAY} files exceeded` },
        { status: 429 }
      )
    }

    const formData = await request.formData()
    const file = formData.get('file') as File

    if (!file) {
      return NextResponse.json({ error: 'No file provided' }, { status: 400 })
    }

    // Validate file type
    if (!ALLOWED_FILE_TYPES.includes(file.type)) {
      return NextResponse.json(
        { error: 'File type not supported. Please upload PDF, Word, Excel, or text files.' },
        { status: 400 }
      )
    }

    // Validate file size
    if (file.size > MAX_FILE_SIZE) {
      return NextResponse.json(
        { error: 'File size too large. Maximum size is 10MB.' },
        { status: 400 }
      )
    }

    // Create uploads directory if it doesn't exist
    const uploadsDir = join(process.cwd(), 'uploads', userId)
    if (!existsSync(uploadsDir)) {
      await mkdir(uploadsDir, { recursive: true })
    }

    // Generate unique filename
    const timestamp = Date.now()
    const fileExtension = file.name.split('.').pop()
    const fileName = `${timestamp}.${fileExtension}`
    const filePath = join(uploadsDir, fileName)

    // Save file
    const bytes = await file.arrayBuffer()
    const buffer = Buffer.from(bytes)
    await writeFile(filePath, buffer)

    // Update upload count
    userUploads.count++
    uploadCounts.set(userKey, userUploads)

    // Process document using the existing FastAPI backend
    const extractedText = await processDocumentWithBackend(file, filePath, fileName, file.type)

    return NextResponse.json({
      success: true,
      fileName: file.name,
      filePath,
      extractedText,
      uploadCount: userUploads.count,
      remainingUploads: MAX_UPLOADS_PER_DAY - userUploads.count
    })

  } catch (error) {
    console.error('Upload error:', error)
    return NextResponse.json(
      { error: 'Failed to upload file' },
      { status: 500 }
    )
  }
}

async function processDocumentWithBackend(file: File, filePath: string, fileName: string, mimeType: string): Promise<string> {
  try {
    const pythonBackendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
    
    // Create FormData to send to FastAPI backend
    const formData = new FormData()
    formData.append('file', file)
    formData.append('country', 'nigeria')
    formData.append('document_type', 'legal_document')

    const response = await fetch(`${pythonBackendUrl}/api/documents/upload`, {
      method: 'POST',
      body: formData
    })

    if (response.ok) {
      const result = await response.json()
      return result.content || `Document content extracted from ${fileName}`
    } else {
      console.log('FastAPI backend not available, using local processing')
      return await processDocumentLocally(filePath, fileName, mimeType)
    }
  } catch (error) {
    console.error('Document processing error:', error)
    return await processDocumentLocally(filePath, fileName, mimeType)
  }
}

async function processDocumentLocally(filePath: string, fileName: string, mimeType: string): Promise<string> {
  // Local document processing logic
  // This would use libraries like pdf-parse, mammoth, etc.
  
  const mockExtractedText = `Document Analysis for ${fileName}

This is a legal document that has been processed locally. The document contains information relevant to Nigerian law and legal procedures.

Key points identified:
- Legal terminology and references
- Procedural requirements
- Relevant statutes and regulations
- Potential legal implications

For comprehensive analysis, please ensure the Python backend is properly configured and running at ${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}.`

  return mockExtractedText
}
