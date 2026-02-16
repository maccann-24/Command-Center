import { NextRequest, NextResponse } from 'next/server'
import { supabase } from '@/lib/supabase'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    
    const { session_id, role, content } = body
    if (!session_id || !role || !content) {
      return NextResponse.json(
        { error: 'session_id, role, and content are required' },
        { status: 400 }
      )
    }
    
    if (!['user', 'assistant'].includes(role)) {
      return NextResponse.json(
        { error: 'role must be "user" or "assistant"' },
        { status: 400 }
      )
    }

    const { data, error } = await supabase
      .from('messages')
      .insert({
        session_id,
        role,
        content,
        timestamp: new Date().toISOString()
      })
      .select()
      .single()

    if (error) {
      return NextResponse.json(
        { error: error.message },
        { status: 500 }
      )
    }

    return NextResponse.json({ 
      success: true,
      message: data 
    }, { status: 201 })

  } catch (error: any) {
    return NextResponse.json(
      { error: error.message || 'Internal server error' },
      { status: 500 }
    )
  }
}
