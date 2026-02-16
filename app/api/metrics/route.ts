import { NextRequest, NextResponse } from 'next/server'
import { supabase } from '@/lib/supabase'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    
    const { session_id, tokens_input, tokens_output, tokens_total, cost, duration_ms } = body
    if (!session_id) {
      return NextResponse.json(
        { error: 'session_id is required' },
        { status: 400 }
      )
    }

    const { data, error } = await supabase
      .from('metrics')
      .insert({
        session_id,
        tokens_input: tokens_input || 0,
        tokens_output: tokens_output || 0,
        tokens_total: tokens_total || 0,
        cost: cost || 0,
        duration_ms: duration_ms || null
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
      metric: data 
    }, { status: 201 })

  } catch (error: any) {
    return NextResponse.json(
      { error: error.message || 'Internal server error' },
      { status: 500 }
    )
  }
}
