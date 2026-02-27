import { NextRequest, NextResponse } from "next/server"
import { getSupabaseAdmin } from "@/lib/supabaseAdmin"

export async function POST(req: NextRequest) {
  try {
    const supabaseAdmin = getSupabaseAdmin()
    const body = await req.json()
    const { taskId } = body as { taskId?: string }

    if (!taskId) {
      return NextResponse.json({ error: "taskId is required" }, { status: 400 })
    }

    // Fetch the task
    const { data: task, error: fetchError } = await supabaseAdmin
      .from("tasks")
      .select("*")
      .eq("id", taskId)
      .single()

    if (fetchError || !task) {
      return NextResponse.json(
        { error: fetchError?.message ?? "Task not found" },
        { status: 404 }
      )
    }

    const now = new Date().toISOString()
    const previousStatus = task.status

    // Build update payload — try to set completed_at if the column exists
    const updatePayload: Record<string, unknown> = {
      status: "done",
      updated_at: now,
    }

    // Attempt to set completed_at (column may or may not exist)
    try {
      const { error: completedAtError } = await supabaseAdmin
        .from("tasks")
        .update({ ...updatePayload, completed_at: now })
        .eq("id", taskId)

      if (completedAtError) {
        // Column likely doesn't exist — fall back without it
        const { error: fallbackError } = await supabaseAdmin
          .from("tasks")
          .update(updatePayload)
          .eq("id", taskId)

        if (fallbackError) throw fallbackError
      }
    } catch (updateErr) {
      throw updateErr
    }

    // Log to task_history
    const { error: historyError } = await supabaseAdmin
      .from("task_history")
      .insert({
        task_id: taskId,
        action: "status_change",
        changed_by: "manual",
        changes: {
          from: previousStatus,
          to: "done",
          timestamp: now,
        },
        created_at: now,
      })

    if (historyError) {
      console.warn("task_history insert failed:", historyError.message)
    }

    // Trigger momentum recalculation for remaining queued tasks
    try {
      const baseUrl =
        process.env.NEXT_PUBLIC_APP_URL ||
        (process.env.VERCEL_URL ? `https://${process.env.VERCEL_URL}` : null) ||
        "http://localhost:3000"

      await fetch(`${baseUrl}/api/tasks/calculate-momentum`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      })
    } catch (momentumErr) {
      // Non-fatal
      console.warn("Momentum recalculation failed:", momentumErr)
    }

    return NextResponse.json({
      success: true,
      task: { ...task, status: "done", updated_at: now },
    })
  } catch (err) {
    const message = err instanceof Error ? err.message : "Unknown error"
    return NextResponse.json({ error: message }, { status: 500 })
  }
}
