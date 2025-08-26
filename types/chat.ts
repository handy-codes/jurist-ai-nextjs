export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  references?: {
    laws: string[]
    cases: string[]
  }
}

export interface ChatSession {
  id: string
  title: string
  createdAt: Date
  updatedAt?: Date
}

// New: Conversation State Management
export interface ConversationState {
  sessionId: string
  userId: string
  currentCase: {
    incidentType: 'search' | 'arrest' | 'seizure' | 'assault' | 'other'
    timeline: Array<{
      date: Date
      event: string
      details: string
    }>
    legalIssues: string[]
    evidence: string[]
    parties: {
      victim: string
      perpetrators: string[]
      witnesses: string[]
    }
    location: string
    jurisdiction: string
  }
  conversationHistory: Message[]
  legalContext: {
    applicableLaws: string[]
    precedents: string[]
    jurisdiction: string
    currentStage: 'fact_gathering' | 'legal_analysis' | 'next_steps' | 'follow_up'
  }
  userIntent: {
    type: 'seeking_advice' | 'providing_update' | 'asking_clarification' | 'seeking_action'
    confidence: number
  }
}

export interface Feedback {
  messageId: string
  rating: number
  isHelpful: boolean
  feedbackText?: string
}

export interface Country {
  code: string
  name: string
  flag: string
}

export interface LegalDocument {
  id: string
  title: string
  content: string
  country: string
  documentType: string
  uploadedAt: Date
  userId: string
}

export interface Template {
  id: string
  name: string
  description: string
  category: string
  parameters: TemplateParameter[]
}

export interface TemplateParameter {
  name: string
  type: 'text' | 'number' | 'date' | 'select'
  label: string
  required: boolean
  options?: string[]
}

// New: Context Analysis Types
export interface ContextUpdate {
  newFacts: string[]
  timelineUpdates: Array<{
    date: Date
    event: string
    details: string
  }>
  legalIssues: string[]
  evidence: string[]
  parties: {
    victim?: string
    perpetrators?: string[]
    witnesses?: string[]
  }
}

export interface ResponseStrategy {
  type: 'initial_advice' | 'follow_up' | 'clarification' | 'legal_action' | 'summary'
  context: {
    previousAdvice: string[]
    newInformation: string[]
    legalProgress: string
  }
  response: {
    acknowledgment: string
    legalAnalysis: string
    nextSteps: string[]
    warnings: string[]
  }
}
