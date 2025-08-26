import { NextRequest, NextResponse } from 'next/server'
import { ConversationManager } from '@/services/conversationManager'

const conversationManager = new ConversationManager()

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const sessionId = searchParams.get('session_id') || 'default_session'
    const summary = conversationManager.getConversationSummary(sessionId)
    return NextResponse.json({ sessionId, summary })
  } catch (error) {
    console.error('Error fetching summary:', error)
    return NextResponse.json({ error: 'Failed to fetch summary' }, { status: 500 })
  }
}
