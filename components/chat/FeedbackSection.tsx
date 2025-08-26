'use client'

import { useState } from 'react'
import { ThumbsUp, ThumbsDown, MessageSquare } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { useToast } from '@/hooks/useToast'

interface FeedbackSectionProps {
  messageId: string
}

export function FeedbackSection({ messageId }: FeedbackSectionProps) {
  const [feedbackText, setFeedbackText] = useState('')
  const [hasSubmitted, setHasSubmitted] = useState(false)
  const { toast } = useToast()

  const handleFeedback = async (rating: number, isHelpful: boolean) => {
    try {
      const response = await fetch('/api/feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messageId,
          rating,
          isHelpful,
        }),
      })

      if (response.ok) {
        toast({
          title: 'Thank you!',
          description: 'Your feedback helps us improve JuristAI.',
        })
        setHasSubmitted(true)
      }
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to submit feedback. Please try again.',
        variant: 'destructive',
      })
    }
  }

  const handleTextFeedback = async () => {
    if (!feedbackText.trim()) return

    try {
      const response = await fetch('/api/feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messageId,
          rating: 0,
          isHelpful: false,
          feedbackText,
        }),
      })

      if (response.ok) {
        toast({
          title: 'Feedback received!',
          description: 'Thank you for helping improve JuristAI.',
        })
        setFeedbackText('')
        setHasSubmitted(true)
      }
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to submit feedback. Please try again.',
        variant: 'destructive',
      })
    }
  }

  if (hasSubmitted) {
    return null
  }

  return (
    <div className="border-t bg-[#292A2D] p-3">
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm font-medium">Was this answer helpful?</span>
        
        <div className="flex items-center gap-1">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => handleFeedback(5, true)}
            className="flex items-center gap-1 h-8 px-2"
          >
            <ThumbsUp className="w-4 h-4" />
            Yes
          </Button>
          
          <Button
            variant="ghost"
            size="sm"
            onClick={() => handleFeedback(1, false)}
            className="flex items-center gap-1 h-8 px-2"
          >
            <ThumbsDown className="w-4 h-4" />
            No
          </Button>
        </div>
      </div>
      
      <div className="flex gap-2">
        <Input
          placeholder="How can I improve? I'm still learning Nigerian law..."
          value={feedbackText}
          onChange={(e) => setFeedbackText(e.target.value)}
          className="flex-1 h-8 text-sm"
        />
        <Button
          size="sm"
          onClick={handleTextFeedback}
          disabled={!feedbackText.trim()}
          className="h-8 px-3"
        >
          <MessageSquare className="w-4 h-4 mr-1" />
          Submit
        </Button>
      </div>
    </div>
  )
}
