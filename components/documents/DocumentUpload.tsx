'use client'

import { useState, useRef } from 'react'
import { Upload, FileText, Trash2, Eye, Download } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { useToast } from '@/hooks/useToast'
import { useCountryStore } from '@/hooks/useCountryStore'

interface Document {
  id: string
  filename: string
  document_type: string
  country: string
  uploaded_at: string
  status: string
}

interface DocumentUploadProps {
  onUploadSuccess?: () => void
}

export function DocumentUpload({ onUploadSuccess }: DocumentUploadProps) {
  const [isUploading, setIsUploading] = useState(false)
  const [documents, setDocuments] = useState<Document[]>([])
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const { selectedCountry } = useCountryStore()
  const { toast } = useToast()

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      if (file.type !== 'application/pdf') {
        toast({
          title: 'Invalid file type',
          description: 'Please select a PDF file',
          variant: 'destructive'
        })
        return
      }
      
      if (file.size > 50 * 1024 * 1024) {
        toast({
          title: 'File too large',
          description: 'File size must be less than 50MB',
          variant: 'destructive'
        })
        return
      }
      
      setSelectedFile(file)
    }
  }

  const handleUpload = async () => {
    if (!selectedFile) return

    setIsUploading(true)
    
    try {
      const formData = new FormData()
      formData.append('file', selectedFile)
      formData.append('country', selectedCountry)
      formData.append('document_type', 'legal_document')

      const response = await fetch('/api/documents/upload', {
        method: 'POST',
        body: formData,
      })

      if (response.ok) {
        const result = await response.json()
        
        toast({
          title: 'Upload successful!',
          description: `Document processed with ${result.chunks_processed} chunks`,
          variant: 'success'
        })
        
        setSelectedFile(null)
        if (fileInputRef.current) {
          fileInputRef.current.value = ''
        }
        
        onUploadSuccess?.()
        loadDocuments()
      } else {
        const error = await response.json()
        throw new Error(error.detail || 'Upload failed')
      }
    } catch (error) {
      toast({
        title: 'Upload failed',
        description: error instanceof Error ? error.message : 'An error occurred',
        variant: 'destructive'
      })
    } finally {
      setIsUploading(false)
    }
  }

  const loadDocuments = async () => {
    try {
      const response = await fetch('/api/documents/list')
      if (response.ok) {
        const data = await response.json()
        setDocuments(data.documents)
      }
    } catch (error) {
      console.error('Error loading documents:', error)
    }
  }

  const deleteDocument = async (documentId: string) => {
    try {
      const response = await fetch(`/api/documents/${documentId}`, {
        method: 'DELETE',
      })

      if (response.ok) {
        toast({
          title: 'Document deleted',
          description: 'Document and all chunks removed successfully',
          variant: 'success'
        })
        loadDocuments()
      } else {
        throw new Error('Failed to delete document')
      }
    } catch (error) {
      toast({
        title: 'Delete failed',
        description: 'Failed to delete document',
        variant: 'destructive'
      })
    }
  }

  return (
    <div className="space-y-6">
      {/* Upload Section */}
      <div className="border-2 border-dashed border-gray-300 rounded-lg p-6">
        <div className="text-center">
          <Upload className="mx-auto h-12 w-12 text-gray-400" />
          <div className="mt-4">
            <label htmlFor="file-upload" className="cursor-pointer">
              <span className="mt-2 block text-sm font-medium text-gray-900">
                Upload Legal Document
              </span>
              <span className="mt-1 block text-xs text-gray-500">
                PDF files only, max 50MB
              </span>
            </label>
            <input
              id="file-upload"
              ref={fileInputRef}
              name="file-upload"
              type="file"
              className="sr-only"
              accept=".pdf"
              onChange={handleFileSelect}
            />
          </div>
          
          {selectedFile && (
            <div className="mt-4">
              <div className="flex items-center justify-center gap-2 text-sm text-gray-600">
                <FileText className="h-4 w-4" />
                {selectedFile.name}
              </div>
              <Button
                onClick={handleUpload}
                disabled={isUploading}
                className="mt-2"
              >
                {isUploading ? 'Processing...' : 'Upload Document'}
              </Button>
            </div>
          )}
        </div>
      </div>

      {/* Documents List */}
      <div>
        <h3 className="text-lg font-medium mb-4">Uploaded Documents</h3>
        <div className="space-y-3">
          {documents.map((doc) => (
            <div
              key={doc.id}
              className="flex items-center justify-between p-4 border rounded-lg bg-gray-50 dark:bg-gray-800"
            >
              <div className="flex items-center gap-3">
                <FileText className="h-5 w-5 text-blue-500" />
                <div>
                  <div className="font-medium">{doc.filename}</div>
                  <div className="text-sm text-gray-500">
                    {doc.country} • {doc.document_type} • {new Date(doc.uploaded_at).toLocaleDateString()}
                  </div>
                </div>
              </div>
              
              <div className="flex items-center gap-2">
                <span className={`px-2 py-1 text-xs rounded-full ${
                  doc.status === 'processed' 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-yellow-100 text-yellow-800'
                }`}>
                  {doc.status}
                </span>
                
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => deleteDocument(doc.id)}
                  className="text-red-500 hover:text-red-700"
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            </div>
          ))}
          
          {documents.length === 0 && (
            <div className="text-center py-8 text-gray-500">
              No documents uploaded yet
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
