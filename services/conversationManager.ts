import { ConversationState, ContextUpdate, Message, ResponseStrategy } from '@/types/chat'
import { getApplicableLawTitles } from '@/services/legalKnowledge'

export class ConversationManager {
  private sessionStore: Map<string, ConversationState> = new Map()

  // Initialize or retrieve conversation state
  getOrCreateState(sessionId: string, userId: string): ConversationState {
    if (!this.sessionStore.has(sessionId)) {
      const initialState: ConversationState = {
        sessionId,
        userId,
        currentCase: {
          incidentType: 'other',
          timeline: [],
          legalIssues: [],
          evidence: [],
          parties: {
            victim: '',
            perpetrators: [],
            witnesses: []
          },
          location: '',
          jurisdiction: 'Nigeria'
        },
        conversationHistory: [],
        legalContext: {
          applicableLaws: [],
          precedents: [],
          jurisdiction: 'Nigeria',
          currentStage: 'fact_gathering'
        },
        userIntent: {
          type: 'seeking_advice',
          confidence: 0.5
        }
      }
      this.sessionStore.set(sessionId, initialState)
    }
    return this.sessionStore.get(sessionId)!
  }

  // Update conversation state with new information
  updateState(sessionId: string, message: Message, contextUpdate: ContextUpdate): ConversationState {
    const state = this.getOrCreateState(sessionId, message.role === 'user' ? 'user' : 'assistant')
    
    // Update conversation history
    state.conversationHistory.push(message)
    
    // Update case information
    if (contextUpdate.newFacts.length > 0) {
      // Extract incident type from new facts
      const incidentKeywords = {
        search: ['search', 'searched', 'phone', 'device', 'laptop'],
        arrest: ['arrest', 'arrested', 'detained', 'custody'],
        seizure: ['seized', 'seizure', 'confiscated', 'taken'],
        assault: ['slapped', 'hit', 'beaten', 'assault', 'force', 'violence']
      }
      
      for (const [type, keywords] of Object.entries(incidentKeywords)) {
        if (keywords.some(keyword => 
          contextUpdate.newFacts.some(fact => 
            fact.toLowerCase().includes(keyword)
          )
        )) {
          state.currentCase.incidentType = type as any
          break
        }
      }
    }

    // Update timeline
    if (contextUpdate.timelineUpdates.length > 0) {
      state.currentCase.timeline.push(...contextUpdate.timelineUpdates)
    }

    // Update legal issues
    if (contextUpdate.legalIssues.length > 0) {
      state.currentCase.legalIssues.push(...contextUpdate.legalIssues)
    }

    // Update evidence
    if (contextUpdate.evidence.length > 0) {
      state.currentCase.evidence.push(...contextUpdate.evidence)
    }

    // Update parties
    if ((contextUpdate.parties as any).victim) {
      state.currentCase.parties.victim = (contextUpdate.parties as any).victim
    }
    if ((contextUpdate.parties as any).perpetrators?.length) {
      state.currentCase.parties.perpetrators.push(...(contextUpdate.parties as any).perpetrators)
    }
    if ((contextUpdate.parties as any).witnesses?.length) {
      state.currentCase.parties.witnesses.push(...(contextUpdate.parties as any).witnesses)
    }

    // Update legal context based on incident type
    this.updateLegalContext(state)

    // Update conversation stage
    this.updateConversationStage(state)

    this.sessionStore.set(sessionId, state)
    return state
  }

  private updateLegalContext(state: ConversationState) {
    const enriched = getApplicableLawTitles(state.currentCase.incidentType as any)
    const applicableLaws = enriched || []
    state.legalContext.applicableLaws = [...new Set([...state.legalContext.applicableLaws, ...applicableLaws])]
  }

  private updateConversationStage(state: ConversationState) {
    const messageCount = state.conversationHistory.length
    const hasTimeline = state.currentCase.timeline.length > 0
    const hasLegalIssues = state.currentCase.legalIssues.length > 0

    if (messageCount <= 2) {
      state.legalContext.currentStage = 'fact_gathering'
    } else if (hasTimeline && hasLegalIssues) {
      state.legalContext.currentStage = 'legal_analysis'
    } else if (state.legalContext.currentStage === 'legal_analysis') {
      state.legalContext.currentStage = 'next_steps'
    }
  }

  // Analyze user intent from message
  analyzeUserIntent(message: string): { type: string; confidence: number } {
    const intentKeywords = {
      seeking_advice: ['what should', 'what can', 'how do', 'advice', 'help'],
      providing_update: ['happened', 'occurred', 'then', 'after', 'later'],
      asking_clarification: ['what does', 'mean', 'explain', 'clarify'],
      seeking_action: ['file', 'report', 'sue', 'complain', 'take action']
    }

    const messageLower = message.toLowerCase()
    let maxConfidence = 0
    let detectedIntent = 'seeking_advice'

    for (const [intent, keywords] of Object.entries(intentKeywords)) {
      const matches = keywords.filter(keyword => messageLower.includes(keyword)).length
      const confidence = matches / keywords.length
      if (confidence > maxConfidence) {
        maxConfidence = confidence
        detectedIntent = intent
      }
    }

    return { type: detectedIntent, confidence: maxConfidence }
  }

  // Generate response strategy based on current state
  generateResponseStrategy(state: ConversationState, userMessage: string): ResponseStrategy {
    const intent = this.analyzeUserIntent(userMessage)
    const previousAdvice = state.conversationHistory
      .filter(msg => msg.role === 'assistant')
      .map(msg => msg.content)

    const strategy: ResponseStrategy = {
      type: 'initial_advice',
      context: {
        previousAdvice,
        newInformation: [],
        legalProgress: state.legalContext.currentStage
      },
      response: {
        acknowledgment: '',
        legalAnalysis: '',
        nextSteps: [],
        warnings: []
      }
    }

    // Determine response type based on stage and intent
    if (state.legalContext.currentStage === 'fact_gathering') {
      strategy.type = 'initial_advice'
    } else if (intent.type === 'providing_update') {
      strategy.type = 'follow_up'
    } else if (intent.type === 'asking_clarification') {
      strategy.type = 'clarification'
    } else if (intent.type === 'seeking_action') {
      strategy.type = 'legal_action'
    }

    return strategy
  }

  // Get conversation summary
  getConversationSummary(sessionId: string): string {
    const state = this.sessionStore.get(sessionId)
    if (!state) return 'No conversation found'

    return `
Case Summary:
- Incident Type: ${state.currentCase.incidentType}
- Timeline Events: ${state.currentCase.timeline.length}
- Legal Issues: ${state.currentCase.legalIssues.join(', ')}
- Current Stage: ${state.legalContext.currentStage}
- Applicable Laws: ${state.legalContext.applicableLaws.length}
    `.trim()
  }
}
