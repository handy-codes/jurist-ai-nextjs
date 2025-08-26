'use client'

import { useEffect, useState, useRef } from 'react'
import { Message } from '@/types/chat'
import { Markdown } from '@/components/ui/Markdown'
import { References } from './References'
import { User, Bot } from 'lucide-react'
import { motion } from 'framer-motion'

interface ChatMessageProps {
  message: Message
  isLatestAssistantMessage?: boolean
}

export function ChatMessage({ message, isLatestAssistantMessage = false }: ChatMessageProps) {
  const isUser = message.role === 'user'
  const [displayText, setDisplayText] = useState<string>(message.content)
  const [hasAnimated, setHasAnimated] = useState(false)
  const messageRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (isUser) {
      setDisplayText(message.content)
      return
    }

    // Only animate if this is the latest assistant message and hasn't been animated before
    if (isLatestAssistantMessage && !hasAnimated) {
      const text = message.content
      let i = 0
      setDisplayText('')
      
      const interval = setInterval(() => {
        i += Math.max(1, Math.floor(text.length / 200)) // speed scales with length
        setDisplayText(text.slice(0, i))
        if (i >= text.length) {
          clearInterval(interval)
          setHasAnimated(true)
        }
      }, 15)
      
      return () => clearInterval(interval)
    } else {
      // For non-latest messages or already animated, show full text immediately
      setDisplayText(message.content)
    }
  }, [message.content, isUser, isLatestAssistantMessage, hasAnimated])

  return (
    <motion.div
      ref={messageRef}
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}
    >
      <div className={`flex items-start gap-3 max-w-[80%] ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
        <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
          isUser ? 'bg-blue-500' : 'bg-gray-600'
        }`}>
          {isUser ? <User className="w-4 h-4 text-white text-[10px] text-justify" /> : <Bot className="w-4 h-4 text-white text-[10px] text-justify" />}
        </div>
        
        <div className={`rounded-lg p-3 ${
          isUser 
            ? 'bg-[#303030] text-white text-[10px] text-justify' 
            : 'bg-[#212121] text-white text-[10px] text-justify'
        }`}>
          <div className="text-lg leading-relaxed">
            <Markdown content={displayText} />
          </div>
          
          {message.references && 
           (message.references as any).laws && 
           (message.references as any).cases && 
           ((message.references as any).laws.length > 0 || (message.references as any).cases.length > 0) && (
            <References references={message.references as any} />
          )}
        </div>
      </div>
    </motion.div>
  )
}
