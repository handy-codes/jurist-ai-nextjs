import { NextRequest, NextResponse } from 'next/server'
import { loadMessages } from '@/lib/db'

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const sessionId = searchParams.get('session_id') || 'default_session'

    const history = loadMessages(sessionId, 100)
    return NextResponse.json(history)
  } catch (error) {
    console.error('Error fetching chat history:', error)
    return NextResponse.json(
      { error: 'Failed to fetch chat history' },
      { status: 500 }
    )
  }
}
