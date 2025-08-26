import { create } from 'zustand'
import { Message, ChatSession } from '@/types/chat'

interface ChatState {
  messages: Message[]
  sessions: ChatSession[]
  currentSession: ChatSession | null
  isLoading: boolean
  initializeChat: (userId: string) => void
  addMessage: (message: Message) => void
  sendMessage: (content: string, userId?: string) => Promise<void>
  createSession: (title: string) => void
  deleteSession: (sessionId: string) => void
  setCurrentSession: (sessionId: string) => void
  loadSession: (sessionId: string) => void
}

export const useChatStore = create<ChatState>((set, get) => ({
  messages: [],
  sessions: [],
  currentSession: null,
  isLoading: false,

  initializeChat: async (userId: string) => {
    try {
      // Load chat sessions from API
      const response = await fetch('/api/chat/sessions')
      if (response.ok) {
        const sessions = await response.json()
        set({ sessions })
        
        if (sessions.length > 0) {
          const session = sessions[0]
          set({ currentSession: session })
          get().loadSession(session.id)
        } else {
          // Create a default session if none
          const createRes = await fetch('/api/chat/sessions', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title: 'Legal Consultation' })
          })
          if (createRes.ok) {
            const newSession = await createRes.json()
            set({ sessions: [newSession], currentSession: newSession })
          }
        }
      }
    } catch (error) {
      console.error('Failed to initialize chat:', error)
      // Create a local default session if API fails
      const defaultSession: ChatSession = {
        id: 'default_session',
        title: 'Legal Consultation',
        createdAt: new Date(),
      }
      set({ sessions: [defaultSession], currentSession: defaultSession })
    }
  },

  addMessage: (message: Message) => {
    set((state) => ({
      messages: [...(Array.isArray(state.messages) ? state.messages : []), message]
    }))
  },

  sendMessage: async (content: string, userId?: string) => {
    set({ isLoading: true })
    
    try {
      const sessionId = get().currentSession?.id || 'default_session'
      const response = await fetch('/api/chat/send', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          content,
          country: 'nigeria',
          sessionId,
          userId: userId || 'anonymous'
        }),
      })

      if (response.ok) {
        const aiMessage = await response.json()
        get().addMessage(aiMessage)
      } else {
        throw new Error('Failed to send message')
      }
    } catch (error) {
      console.error('Error sending message:', error)
      // Add error message to chat
      get().addMessage({
        id: Date.now().toString(),
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date(),
      })
    } finally {
      set({ isLoading: false })
    }
  },

  createSession: async (title: string) => {
    try {
      const response = await fetch('/api/chat/sessions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title })
      })
      
      if (response.ok) {
        const newSession = await response.json()
        set((state) => ({
          sessions: [...state.sessions, newSession],
          currentSession: newSession,
          messages: [],
        }))
      } else {
        // Fallback to local session creation
        const newSession: ChatSession = {
          id: Date.now().toString(),
          title,
          createdAt: new Date(),
        }
        set((state) => ({
          sessions: [...state.sessions, newSession],
          currentSession: newSession,
          messages: [],
        }))
      }
    } catch (error) {
      console.error('Failed to create session:', error)
      // Fallback to local session creation
      const newSession: ChatSession = {
        id: Date.now().toString(),
        title,
        createdAt: new Date(),
      }
      set((state) => ({
        sessions: [...state.sessions, newSession],
        currentSession: newSession,
        messages: [],
      }))
    }
  },

  deleteSession: (sessionId: string) => {
    set((state) => ({
      sessions: state.sessions.filter(s => s.id !== sessionId),
      currentSession: state.currentSession?.id === sessionId 
        ? state.sessions[0] || null 
        : state.currentSession,
      messages: state.currentSession?.id === sessionId ? [] : state.messages,
    }))
  },

  setCurrentSession: (sessionId: string) => {
    const session = get().sessions.find(s => s.id === sessionId)
    if (session) {
      set({ currentSession: session })
      get().loadSession(sessionId)
    }
  },

  loadSession: async (sessionId: string) => {
    try {
      const response = await fetch(`/api/chat/history?session_id=${sessionId}`)
      if (response.ok) {
        const messages = await response.json()
        set({ messages: Array.isArray(messages) ? messages : [] })
      } else {
        console.error('Failed to load session history')
        set({ messages: [] })
      }
    } catch (error) {
      console.error('Failed to load session:', error)
      set({ messages: [] })
    }
  },
}))
