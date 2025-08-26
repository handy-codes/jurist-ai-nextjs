'use client'

import { useUser } from '@clerk/nextjs'
import { redirect } from 'next/navigation'
import { DocumentUpload } from '@/components/documents/DocumentUpload'
import { LoadingSpinner } from '@/components/ui/LoadingSpinner'

export default function DocumentsPage() {
  const { user, isLoaded } = useUser()

  if (!isLoaded) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  if (!user) {
    redirect('/sign-in')
  }

  return (
    <div className="container mx-auto p-6">
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-foreground mb-2">
            Document Management
          </h1>
          <p className="text-muted-foreground">
            Upload and manage legal documents to enhance JuristAI's knowledge base
          </p>
        </div>

        <div className="grid gap-8">
          {/* Upload Section */}
          <div className="bg-card border rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Upload Legal Documents</h2>
            <DocumentUpload />
          </div>

          {/* Instructions */}
          <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-blue-900 dark:text-blue-100 mb-3">
              📚 How Document Ingestion Works
            </h3>
            <div className="space-y-3 text-blue-800 dark:text-blue-200">
              <div className="flex items-start gap-3">
                <span className="font-medium">1.</span>
                <span>Upload PDF legal documents (laws, cases, regulations)</span>
              </div>
              <div className="flex items-start gap-3">
                <span className="font-medium">2.</span>
                <span>System extracts text using OCR for scanned documents</span>
              </div>
              <div className="flex items-start gap-3">
                <span className="font-medium">3.</span>
                <span>Documents are chunked into smaller, searchable segments</span>
              </div>
              <div className="flex items-start gap-3">
                <span className="font-medium">4.</span>
                <span>Legal references (laws, cases) are automatically extracted</span>
              </div>
              <div className="flex items-start gap-3">
                <span className="font-medium">5.</span>
                <span>Chunks are embedded and stored in vector database</span>
              </div>
              <div className="flex items-start gap-3">
                <span className="font-medium">6.</span>
                <span>AI uses these chunks to provide accurate, referenced responses</span>
              </div>
            </div>
          </div>

          {/* Best Practices */}
          <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-green-900 dark:text-green-100 mb-3">
              ✅ Best Practices
            </h3>
            <ul className="space-y-2 text-green-800 dark:text-green-200">
              <li>• Upload official legal documents (Acts, Regulations, Court Judgments)</li>
              <li>• Ensure documents are clear and readable</li>
              <li>• Use descriptive filenames for easy identification</li>
              <li>• Select the correct country jurisdiction</li>
              <li>• Upload documents in chronological order for better context</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}
