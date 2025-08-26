'use client'

import { useState, useRef, useEffect } from 'react'
import { Send, Paperclip, Mic, MicOff, Square, FileText, X } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { useToast } from '@/hooks/useToast'

interface ChatInputProps {
  onSend: (message: string) => void
  isLoading: boolean
}

export function ChatInput({ onSend, isLoading }: ChatInputProps) {
  const [message, setMessage] = useState('')
  const [isRecording, setIsRecording] = useState(false)
  const [hasPermission, setHasPermission] = useState<boolean | null>(null)
  const [uploadedFiles, setUploadedFiles] = useState<Array<{ name: string; content: string }>>([])
  const [isUploading, setIsUploading] = useState(false)
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const recognitionRef = useRef<any>(null)
  const { toast } = useToast()

  // Initialize speech recognition
  useEffect(() => {
    if (typeof window !== 'undefined' && 'webkitSpeechRecognition' in window) {
      const SpeechRecognition = (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition
      recognitionRef.current = new SpeechRecognition()
      recognitionRef.current.continuous = true
      recognitionRef.current.interimResults = true
      recognitionRef.current.lang = 'en-US'

      recognitionRef.current.onresult = (event: any) => {
        let finalTranscript = ''
        for (let i = event.resultIndex; i < event.results.length; i++) {
          if (event.results[i].isFinal) {
            finalTranscript += event.results[i][0].transcript
          }
        }
        if (finalTranscript) {
          setMessage(prev => prev + finalTranscript)
        }
      }

      recognitionRef.current.onerror = (event: any) => {
        console.error('Speech recognition error:', event.error)
        setIsRecording(false)
      }

      recognitionRef.current.onend = () => {
        setIsRecording(false)
      }
    }
  }, [])

  const requestMicrophonePermission = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      stream.getTracks().forEach(track => track.stop()) // Stop the stream immediately
      setHasPermission(true)
      return true
    } catch (error) {
      console.error('Microphone permission denied:', error)
      setHasPermission(false)
      return false
    }
  }

  const startRecording = async () => {
    if (!recognitionRef.current) {
      alert('Speech recognition is not supported in this browser.')
      return
    }

    if (hasPermission === null) {
      const granted = await requestMicrophonePermission()
      if (!granted) {
        alert('Microphone permission is required for voice input.')
        return
      }
    }

    if (hasPermission === false) {
      alert('Please enable microphone permission in your browser settings.')
      return
    }

    try {
      recognitionRef.current.start()
      setIsRecording(true)
    } catch (error) {
      console.error('Failed to start recording:', error)
    }
  }

  const stopRecording = () => {
    if (recognitionRef.current && isRecording) {
      recognitionRef.current.stop()
      setIsRecording(false)
    }
  }

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files
    if (!files || files.length === 0) return

    setIsUploading(true)
    
    try {
      for (let i = 0; i < files.length; i++) {
        const file = files[i]
        
        // Validate file type
        const allowedTypes = [
          'application/pdf',
          'application/msword',
          'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
          'application/vnd.ms-excel',
          'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
          'text/plain',
          'application/rtf'
        ]
        
        if (!allowedTypes.includes(file.type)) {
          toast({
            title: 'Invalid file type',
            description: 'Please upload PDF, Word, Excel, or text files only.',
            variant: 'destructive'
          })
          continue
        }

        // Validate file size (10MB limit)
        if (file.size > 10 * 1024 * 1024) {
          toast({
            title: 'File too large',
            description: 'File size must be less than 10MB.',
            variant: 'destructive'
          })
          continue
        }

        const formData = new FormData()
        formData.append('file', file)

        const response = await fetch('/api/upload', {
          method: 'POST',
          body: formData
        })

        if (response.ok) {
          const result = await response.json()
          setUploadedFiles(prev => [...prev, { name: file.name, content: result.extractedText }])
          
          toast({
            title: 'File uploaded successfully',
            description: `${file.name} has been processed and is ready for analysis.`
          })
        } else {
          const error = await response.json()
          toast({
            title: 'Upload failed',
            description: error.error || 'Failed to upload file',
            variant: 'destructive'
          })
        }
      }
    } catch (error) {
      toast({
        title: 'Upload error',
        description: 'An error occurred while uploading the file.',
        variant: 'destructive'
      })
    } finally {
      setIsUploading(false)
      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
    }
  }

  const removeFile = (index: number) => {
    setUploadedFiles(prev => prev.filter((_, i) => i !== index))
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if ((message.trim() || uploadedFiles.length > 0) && !isLoading) {
      let fullMessage = message.trim()
      
      if (uploadedFiles.length > 0) {
        fullMessage += '\n\n**Uploaded Documents:**\n' + 
          uploadedFiles.map(file => `- ${file.name}\n${file.content}`).join('\n\n')
      }
      
      onSend(fullMessage)
      setMessage('')
      setUploadedFiles([])
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`
    }
  }, [message])

  return (
    <div className="space-y-3">
      {/* Uploaded Files Display */}
      {uploadedFiles.length > 0 && (
        <div className="flex flex-wrap gap-2 p-2 bg-[#404045] rounded-lg">
          {uploadedFiles.map((file, index) => (
            <div key={index} className="flex items-center gap-2 bg-[#292A2D] px-3 py-1 rounded-md">
              <FileText className="h-4 w-4 text-blue-400" />
              <span className="text-sm text-white">{file.name}</span>
              <Button
                type="button"
                variant="ghost"
                size="icon"
                onClick={() => removeFile(index)}
                className="h-4 w-4 hover:bg-red-500 hover:text-white"
              >
                <X className="h-3 w-3" />
              </Button>
            </div>
          ))}
        </div>
      )}

      {/* Hidden file input */}
      <input
        ref={fileInputRef}
        type="file"
        multiple
        accept=".pdf,.doc,.docx,.xls,.xlsx,.txt,.rtf"
        onChange={handleFileUpload}
        className="hidden"
      />

      <form onSubmit={handleSubmit} className="flex items-center gap-3 p-3 bg-[#404045] rounded-full focus-within:outline-none">
        <div className="flex-1 relative flex items-center">
          <textarea
            ref={textareaRef}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask a legal question..."
            className="w-full min-h-[40px] max-h-[120px] rounded-md bg-transparent px-3 py-2.5 text-sm shadow-sm transition-colors placeholder:text-muted-foreground focus:outline-none focus:ring-0 disabled:cursor-not-allowed disabled:opacity-50 resize-none"
            disabled={isLoading || isUploading}
          />
          <div className="absolute right-2 flex items-center gap-1">
            <Button
              type="button"
              variant="ghost"
              size="icon"
              className="h-6 w-6"
              disabled={isLoading || isUploading}
              onClick={() => fileInputRef.current?.click()}
              title="Upload document"
            >
              <Paperclip className="h-5 w-5" />
            </Button>
            <Button
              type="button"
              variant={isRecording ? "destructive" : "ghost"}
              size="icon"
              className={`h-6 w-6 ${isRecording ? 'animate-pulse' : ''}`}
              disabled={isLoading || isUploading}
              onClick={isRecording ? stopRecording : startRecording}
              title={isRecording ? 'Stop recording' : 'Start voice input'}
            >
              {isRecording ? <Square className="h-3 w-3" /> : <Mic className="h-5 w-5" />}
            </Button>
          </div>
        </div>
        <Button
          type="submit"
          size="icon"
          disabled={(!message.trim() && uploadedFiles.length === 0) || isLoading || isUploading}
          className="h-10 w-10 flex-shrink-0"
        >
          <Send className="h-4 w-4" />
        </Button>
      </form>
    </div>
  )
}
