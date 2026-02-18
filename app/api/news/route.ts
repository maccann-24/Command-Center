import { NextRequest, NextResponse } from 'next/server'
import { supabase } from '@/lib/supabase'

// Special agent ID for news digest storage
const NEWS_AGENT_NAME = 'News Digest'

async function getOrCreateNewsAgent() {
  const { data: existing } = await supabase
    .from('agents')
    .select('id')
    .eq('name', NEWS_AGENT_NAME)
    .single()

  if (existing) return existing.id

  const { data, error } = await supabase
    .from('agents')
    .insert({ name: NEWS_AGENT_NAME, model: 'system', status: 'idle' })
    .select('id')
    .single()

  if (error) throw new Error(error.message)
  return data.id
}

async function getOrCreateNewsSession(agentId: string) {
  // Find active session for news agent
  const { data: existing } = await supabase
    .from('sessions')
    .select('id')
    .eq('agent_id', agentId)
    .eq('status', 'active')
    .order('start_time', { ascending: false })
    .limit(1)
    .single()

  if (existing) return existing.id

  const { data, error } = await supabase
    .from('sessions')
    .insert({ agent_id: agentId, status: 'active', start_time: new Date().toISOString() })
    .select('id')
    .single()

  if (error) throw new Error(error.message)
  return data.id
}

// GET /api/news — return latest news items
export async function GET() {
  try {
    const { data: agent } = await supabase
      .from('agents')
      .select('id')
      .eq('name', NEWS_AGENT_NAME)
      .single()

    if (!agent) return NextResponse.json({ items: [], date: null })

    const { data: session } = await supabase
      .from('sessions')
      .select('id')
      .eq('agent_id', agent.id)
      .eq('status', 'active')
      .order('start_time', { ascending: false })
      .limit(1)
      .single()

    if (!session) return NextResponse.json({ items: [], date: null })

    // Get the latest digest message (most recent 'assistant' message with JSON content)
    const { data: messages } = await supabase
      .from('messages')
      .select('content, timestamp')
      .eq('session_id', session.id)
      .eq('role', 'assistant')
      .order('timestamp', { ascending: false })
      .limit(1)

    if (!messages || messages.length === 0) return NextResponse.json({ items: [], date: null })

    try {
      const parsed = JSON.parse(messages[0].content)
      return NextResponse.json({
        items: parsed.items || [],
        date: parsed.date || messages[0].timestamp,
      })
    } catch {
      return NextResponse.json({ items: [], date: messages[0].timestamp })
    }
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 })
  }
}

// POST /api/news — store a new digest
// Body: { items: [{headline, summary, source, category, url?}], date?: string }
export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { items, date } = body

    if (!items || !Array.isArray(items)) {
      return NextResponse.json({ error: 'items array is required' }, { status: 400 })
    }

    const agentId = await getOrCreateNewsAgent()
    const sessionId = await getOrCreateNewsSession(agentId)

    const content = JSON.stringify({
      items,
      date: date || new Date().toISOString(),
    })

    const { data, error } = await supabase
      .from('messages')
      .insert({
        session_id: sessionId,
        role: 'assistant',
        content,
        timestamp: new Date().toISOString(),
      })
      .select()
      .single()

    if (error) return NextResponse.json({ error: error.message }, { status: 500 })

    return NextResponse.json({ success: true, message: data }, { status: 201 })
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 })
  }
}
