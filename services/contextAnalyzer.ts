import { ContextUpdate } from '@/types/chat'

export class ContextAnalyzer {
  
  // Extract context from user message
  extractContext(message: string, existingContext?: any): ContextUpdate {
    const contextUpdate: ContextUpdate = {
      newFacts: [],
      timelineUpdates: [],
      legalIssues: [],
      evidence: [],
      parties: {
        victim: '',
        perpetrators: [],
        witnesses: []
      }
    }

    // Extract facts
    contextUpdate.newFacts = this.extractFacts(message)
    
    // Extract timeline events
    contextUpdate.timelineUpdates = this.extractTimelineEvents(message)
    
    // Extract legal issues
    contextUpdate.legalIssues = this.extractLegalIssues(message)
    
    // Extract evidence
    contextUpdate.evidence = this.extractEvidence(message)
    
    // Extract parties
    contextUpdate.parties = this.extractParties(message)

    return contextUpdate
  }

  private extractFacts(message: string): string[] {
    const facts: string[] = []
    const sentences = message.split(/[.!?]+/).filter(s => s.trim().length > 0)
    
    for (const sentence of sentences) {
      const trimmed = sentence.trim()
      
      // Look for factual statements
      if (this.isFactualStatement(trimmed)) {
        facts.push(trimmed)
      }
    }
    
    return facts
  }

  private isFactualStatement(sentence: string): boolean {
    const factualIndicators = [
      'was', 'were', 'is', 'are', 'had', 'have', 'has',
      'police', 'officer', 'searched', 'arrested', 'seized',
      'slapped', 'hit', 'beaten', 'force', 'violence',
      'phone', 'laptop', 'device', 'property'
    ]
    
    const lowerSentence = sentence.toLowerCase()
    return factualIndicators.some(indicator => lowerSentence.includes(indicator))
  }

  private extractTimelineEvents(message: string): Array<{date: Date; event: string; details: string}> {
    const events: Array<{date: Date; event: string; details: string}> = []
    
    // Look for time indicators
    const timePatterns = [
      /(initially|first|at first|in the beginning)/i,
      /(then|after|later|subsequently|next)/i,
      /(finally|eventually|in the end)/i
    ]
    
    const sentences = message.split(/[.!?]+/).filter(s => s.trim().length > 0)
    
    for (const sentence of sentences) {
      const trimmed = sentence.trim()
      
      for (let i = 0; i < timePatterns.length; i++) {
        if (timePatterns[i].test(trimmed)) {
          const event = this.extractEventFromSentence(trimmed)
          if (event) {
            events.push({
              date: new Date(), // We'll use current date as placeholder
              event: event,
              details: trimmed
            })
          }
          break
        }
      }
    }
    
    return events
  }

  private extractEventFromSentence(sentence: string): string {
    const eventKeywords = {
      'search': ['search', 'searched', 'looking through'],
      'arrest': ['arrest', 'arrested', 'detained', 'taken into custody'],
      'seizure': ['seize', 'seized', 'confiscated', 'taken'],
      'assault': ['slap', 'slapped', 'hit', 'beaten', 'assault', 'force']
    }
    
    const lowerSentence = sentence.toLowerCase()
    
    for (const [eventType, keywords] of Object.entries(eventKeywords)) {
      if (keywords.some(keyword => lowerSentence.includes(keyword))) {
        return eventType
      }
    }
    
    return 'other'
  }

  private extractLegalIssues(message: string): string[] {
    const legalIssues: string[] = []
    const legalKeywords = [
      'right to privacy', 'right to property', 'right to dignity',
      'unlawful search', 'unlawful arrest', 'excessive force',
      'police brutality', 'human rights violation', 'constitutional rights',
      'search warrant', 'due process', 'legal procedure'
    ]
    
    const lowerMessage = message.toLowerCase()
    
    for (const keyword of legalKeywords) {
      if (lowerMessage.includes(keyword)) {
        legalIssues.push(keyword)
      }
    }
    
    return legalIssues
  }

  private extractEvidence(message: string): string[] {
    const evidence: string[] = []
    const evidenceKeywords = [
      'phone', 'laptop', 'device', 'property', 'belongings',
      'witness', 'witnesses', 'camera', 'recording', 'video',
      'document', 'paper', 'receipt', 'medical report'
    ]
    
    const lowerMessage = message.toLowerCase()
    
    for (const keyword of evidenceKeywords) {
      if (lowerMessage.includes(keyword)) {
        evidence.push(keyword)
      }
    }
    
    return evidence
  }

  private extractParties(message: string): {victim: string; perpetrators: string[]; witnesses: string[]} {
    const parties = {
      victim: '',
      perpetrators: [],
      witnesses: []
    }
    
    const lowerMessage = message.toLowerCase()
    
    // Extract victim (usually the user)
    if (lowerMessage.includes('my') || lowerMessage.includes('i was') || lowerMessage.includes('me')) {
      parties.victim = 'User'
    }
    
    // Extract perpetrators
    if (lowerMessage.includes('police') || lowerMessage.includes('officer')) {
      parties.perpetrators.push('Police Officer(s)')
    }
    
    // Extract witnesses
    if (lowerMessage.includes('witness') || lowerMessage.includes('saw') || lowerMessage.includes('observed')) {
      parties.witnesses.push('Witness(es)')
    }
    
    return parties
  }

  // Analyze message sentiment and urgency
  analyzeMessageSentiment(message: string): {sentiment: 'positive' | 'negative' | 'neutral'; urgency: 'low' | 'medium' | 'high'} {
    const negativeWords = ['slapped', 'hit', 'beaten', 'force', 'violence', 'unlawful', 'wrong', 'bad']
    const urgentWords = ['immediately', 'urgent', 'emergency', 'now', 'right away', 'asap']
    
    const lowerMessage = message.toLowerCase()
    
    let sentiment: 'positive' | 'negative' | 'neutral' = 'neutral'
    let urgency: 'low' | 'medium' | 'high' = 'low'
    
    // Analyze sentiment
    const negativeCount = negativeWords.filter(word => lowerMessage.includes(word)).length
    if (negativeCount > 0) {
      sentiment = 'negative'
    }
    
    // Analyze urgency
    const urgentCount = urgentWords.filter(word => lowerMessage.includes(word)).length
    if (urgentCount >= 2) {
      urgency = 'high'
    } else if (urgentCount === 1) {
      urgency = 'medium'
    }
    
    return { sentiment, urgency }
  }

  // Check if message contains new information
  hasNewInformation(message: string, existingContext: any): boolean {
    const newFacts = this.extractFacts(message)
    const newTimeline = this.extractTimelineEvents(message)
    const newLegalIssues = this.extractLegalIssues(message)
    
    return newFacts.length > 0 || newTimeline.length > 0 || newLegalIssues.length > 0
  }
}
