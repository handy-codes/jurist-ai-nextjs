import { NextRequest, NextResponse } from 'next/server'

export async function GET(request: NextRequest) {
  try {
    // Return a default session for now
    const sessions = [
      {
        id: 'default_session',
        title: 'Legal Consultation',
        createdAt: new Date().toISOString()
      }
    ]
    
    return NextResponse.json(sessions)
  } catch (error) {
    console.error('Error fetching chat sessions:', error)
    return NextResponse.json(
      { error: 'Failed to fetch chat sessions' },
      { status: 500 }
    )
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    
    // Create a new session
    const session = {
      id: `session_${Date.now()}`,
      title: body.title || 'New Chat',
      createdAt: new Date().toISOString()
    }
    
    return NextResponse.json(session)
  } catch (error) {
    console.error('Error creating chat session:', error)
    return NextResponse.json(
      { error: 'Failed to create chat session' },
      { status: 500 }
    )
  }
}
