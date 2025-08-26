export interface QaResult {
  id: string
  sessionId: string
  coherenceScore: number // 0-1
  legalRelevanceScore: number // 0-1
  contextUsageScore: number // 0-1
  flags: string[]
  createdAt: string
}

export function evaluateAssistantResponse(params: {
  sessionId: string
  messageId: string
  userContent: string
  assistantContent: string
  applicableLaws: string[]
  stage: string
}): QaResult {
  const { sessionId, messageId, userContent, assistantContent, applicableLaws, stage } = params
  const text = assistantContent.toLowerCase()
  const userLower = userContent.toLowerCase()

  // Heuristics
  const mentionsLaw = applicableLaws.some((law) => text.includes(law.toLowerCase().slice(0, 20)))
  const mentionsNigeria = /nigeria|nigerian|constitution of nigeria|police act/i.test(assistantContent)
  const hasActionables = /(next steps|you should|consider|report|file|seek|consult|document)/i.test(assistantContent)
  const repeatsQuestion = assistantContent.trim().startsWith(userContent.trim().slice(0, 20))
  const lengthOk = assistantContent.length >= 200 && assistantContent.length <= 2200

  const coherenceScore = Math.min(1, (Number(lengthOk) + Number(hasActionables) + Number(!repeatsQuestion)) / 3)
  const legalRelevanceScore = Math.min(1, (Number(mentionsNigeria) + Number(mentionsLaw)) / 2)
  const contextUsageScore = Math.min(1, (stage === 'legal_analysis' || stage === 'next_steps') ? 1 : 0.6)

  const flags: string[] = []
  if (!hasActionables) flags.push('no_actionables')
  if (!mentionsNigeria) flags.push('no_nigeria_context')
  if (!mentionsLaw) flags.push('no_citations')

  return {
    id: `qa_${messageId}`,
    sessionId,
    coherenceScore,
    legalRelevanceScore,
    contextUsageScore,
    flags,
    createdAt: new Date().toISOString(),
  }
}
