import { NextRequest, NextResponse } from 'next/server'
import { supabase } from '@/lib/supabase'

export async function GET() {
  const { data, error } = await supabase.from('agents').select('*').order('created_at')
  if (error) return NextResponse.json({ error: error.message }, { status: 500 })
  return NextResponse.json({ agents: data })
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { name, model, status } = body
    if (!name || !model) {
      return NextResponse.json({ error: 'name and model are required' }, { status: 400 })
    }

    // Upsert by name
    const { data: existing } = await supabase.from('agents').select('id').eq('name', name).single()

    if (existing) {
      const { data, error } = await supabase
        .from('agents')
        .update({ model, status: status || 'active', updated_at: new Date().toISOString() })
        .eq('id', existing.id)
        .select()
        .single()
      if (error) return NextResponse.json({ error: error.message }, { status: 500 })
      return NextResponse.json({ success: true, agent: data, action: 'updated' })
    } else {
      const { data, error } = await supabase
        .from('agents')
        .insert({ name, model, status: status || 'active' })
        .select()
        .single()
      if (error) return NextResponse.json({ error: error.message }, { status: 500 })
      return NextResponse.json({ success: true, agent: data, action: 'created' }, { status: 201 })
    }
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 })
  }
}
