import { NextRequest, NextResponse } from 'next/server'
import { conversationManager, contextAnalyzer } from '@/lib/conversation'
import { saveMessage, saveQaResult } from '@/lib/db'
import { evaluateAssistantResponse } from '@/services/qa'

const GROQ_API_KEY = process.env.GROQ_API_KEY
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

type LawCases = { laws: string[]; cases: string[] }

function cleanAndDedupe(items: string[]): string[] {
  const set = new Set<string>()
  for (const raw of items) {
    if (!raw) continue
    const parts = raw.split(/;+/)
    for (let p of parts) {
      p = p.replace(/^legal basis[:\-]?/i, '').trim()
      if (p.endsWith('.')) p = p.slice(0, -1)
      if (p.length < 6) continue
      p = p.replace(/\s+/g, ' ')
      set.add(p)
    }
  }
  return Array.from(set)
}

function extractReferencesFromText(text: string): LawCases {
  const rawLaws = new Set<string>()
  const rawCases = new Set<string>()
  const lawPatterns = [
    /(constitution of nigeria[^\n\.;]*)/gi,
    /(criminal (procedure|code) act[^\n\.;]*)/gi,
    /(evidence act[^\n\.;]*)/gi,
    /(police act[^\n\.;]*)/gi,
    /(section\s+\d+[A-Za-z\-]*\s+of\s+the\s+[^\n\.;]*)/gi
  ]
  for (const pattern of lawPatterns) {
    const matches = text.match(pattern) || []
    matches.forEach((m) => rawLaws.add(m.trim()))
  }
  const casePatterns = [
    /[A-Z][A-Za-z\-\s]+\s+v\.?\s+[A-Z][A-Za-z\-\s]+\s*\([^\)]*\)/g,
    /[A-Z][A-Za-z\-\s]+\s+v\.?\s+[A-Z][A-Za-z\-\s]+/g
  ]
  for (const pattern of casePatterns) {
    const matches = text.match(pattern) || []
    matches.forEach((m) => rawCases.add(m.trim()))
  }
  const laws = cleanAndDedupe(Array.from(rawLaws)).slice(0, 10)
  const cases = cleanAndDedupe(Array.from(rawCases)).slice(0, 10)
  return { laws, cases }
}

async function callBackend(content: string, country: string) {
  try {
    const res = await fetch(`${API_URL}/api/chat/send`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content, country })
    })
    if (!res.ok) return null
    return await res.json()
  } catch {
    return null
  }
}

async function callGroq(messages: any[]) {
  if (!GROQ_API_KEY) return { ok: false, status: 401, content: '' }
  try {
    const response = await fetch('https://api.groq.com/openai/v1/chat/completions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${GROQ_API_KEY}` },
      body: JSON.stringify({ model: 'llama3-8b-8192', messages, temperature: 0.3, max_tokens: 2000 })
    })
    if (!response.ok) {
      return { ok: false, status: response.status, content: '' }
    }
    const data = await response.json()
    const content: string = data.choices?.[0]?.message?.content || ''
    return { ok: true, status: 200, content }
  } catch (e) {
    return { ok: false, status: 0, content: '' }
  }
}

function isCaseLawQuery(text: string): boolean {
  return /(case|cases|precedent|authorities|judgment|decision)/i.test(text)
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const content: string = body.content || ''
    const sessionId: string = body.sessionId || 'default_session'
    const userId: string = body.userId || 'anonymous'
    const country = body.country || 'nigeria'
    if (!content.trim()) {
      return NextResponse.json({ error: 'Content is required' }, { status: 400 })
    }

    // Proxy to backend RAG first
    const backend = await callBackend(content, country)
    if (backend && backend.content) {
      // Use backend response and references directly
      const assistantMessage = {
        id: backend.id || (Date.now() + 1).toString(),
        role: 'assistant' as const,
        content: backend.content,
        references: backend.references || { laws: [], cases: [] },
        timestamp: new Date().toISOString(),
        sessionId
      }
      return NextResponse.json(assistantMessage)
    }

    // Fallback to local context pipeline (as implemented previously)
    const contextUpdate = contextAnalyzer.extractContext(content)
    const userMessage = { id: Date.now().toString(), role: 'user' as const, content, timestamp: new Date() }
    const state = conversationManager.updateState(sessionId, userMessage, contextUpdate)
    saveMessage({ id: userMessage.id, sessionId, role: 'user', content: userMessage.content, timestamp: userMessage.timestamp.toISOString() })

    const summary = conversationManager.getConversationSummary(sessionId)
    const recent = state.conversationHistory.slice(-6).map((m) => ({ role: m.role, content: m.content }))

    const systemPreamble = `You are a Nigerian legal expert AI assistant. Answer directly and confidently. No apologies or disclaimers. Lead with the rule in one sentence, then targeted analysis and next steps. Cite only what is relevant.`
    const contextualInstructions = `Stage: ${state.legalContext.currentStage}\nIncident: ${state.currentCase.incidentType}\nApplicableLaws: ${state.legalContext.applicableLaws.join('; ') || 'N/A'}\nCaseSummary: ${summary}`

    const modelMessages: any[] = [
      { role: 'system', content: systemPreamble },
      { role: 'system', content: contextualInstructions },
      ...recent,
      { role: 'user', content }
    ]

    const groq = await callGroq(modelMessages)

    let aiResponse: string
    if (!groq.ok) {
      if (isCaseLawQuery(content)) {
        aiResponse = [
          'Yes—Nigerian courts have addressed unlawful searches and privacy; decisions generally treat phone searches without a warrant as presumptively unlawful unless falling within recognized exceptions (lawful arrest with reasonable grounds or genuine exigency).',
          '',
          'What to look for: appellate decisions on s.37 privacy and search/seizure procedure; rulings excluding evidence obtained through unlawful searches under the Evidence Act. When online access is restored, I will list specific case names and brief holdings.',
          '',
          'Next steps: (1) Preserve facts (date/time, officers, what was searched/seized); (2) Engage counsel to assess a rights action and potential exclusion of unlawfully obtained evidence; (3) File complaints with PCRU/NHRC as appropriate.'
        ].join('\n')
      } else {
        aiResponse = [
          'No—police in Nigeria cannot search your phone without a lawful basis. A court-issued warrant is the default; limited exceptions are a search incident to a lawful arrest with reasonable grounds, or genuine exigency (imminent harm or destruction of evidence).',
          '',
          'Legal basis: Constitution (1999) s.37 (privacy); criminal procedure on warrants and searches; Evidence Act (lawful collection); Police Act (powers subject to due process).',
          '',
          'What to do: (1) Ask if you are under arrest and request to see a warrant; (2) If none, calmly state you do not consent; (3) Do not obstruct—note officers/IDs; (4) If force/seizure occurred, document and seek counsel; (5) Consider PCRU/NHRC complaints or court redress.'
        ].join('\n')
      }
    } else {
      aiResponse = groq.content || 'I could not generate a response.'
    }

    let references: LawCases = extractReferencesFromText(aiResponse)
    if (references.laws.length === 0 && state.legalContext.applicableLaws.length > 0) {
      references = { laws: cleanAndDedupe(state.legalContext.applicableLaws.slice(0, 5)), cases: references.cases }
    }

    const assistantMessage = { id: (Date.now() + 1).toString(), role: 'assistant' as const, content: aiResponse, timestamp: new Date(), references }
    conversationManager.updateState(sessionId, assistantMessage as any, { newFacts: [], timelineUpdates: [], legalIssues: [], evidence: [], parties: {} as any })
    saveMessage({ id: assistantMessage.id, sessionId, role: 'assistant', content: assistantMessage.content, timestamp: assistantMessage.timestamp.toISOString() })

    const qa = evaluateAssistantResponse({
      sessionId,
      messageId: assistantMessage.id,
      userContent: content,
      assistantContent: aiResponse,
      applicableLaws: state.legalContext.applicableLaws,
      stage: state.legalContext.currentStage
    })
    saveQaResult({ id: qa.id, sessionId, coherence: qa.coherenceScore, legal: qa.legalRelevanceScore, context: qa.contextUsageScore, flags: qa.flags, createdAt: qa.createdAt })

    console.log('[analytics] send', { sessionId, userId, len: content.length })

    return NextResponse.json({ ...assistantMessage, timestamp: assistantMessage.timestamp.toISOString(), sessionId })
  } catch (error) {
    console.error('Error sending chat message:', error)
    return NextResponse.json({ error: 'Failed to send chat message' }, { status: 500 })
  }
}
