import { NextRequest, NextResponse } from "next/server"
import fs from "fs/promises"
import path from "path"
import { getSupabaseAdmin } from "@/lib/supabaseAdmin"

const PENDING_TASK_PATH = "/home/ubuntu/clawd/pending-task.json"

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

    if (task.status !== "queued") {
      return NextResponse.json(
        { error: `Task is already ${task.status}` },
        { status: 400 }
      )
    }

    // Update task status to in_progress
    const now = new Date().toISOString()
    const { error: updateError } = await supabaseAdmin
      .from("tasks")
      .update({ status: "in_progress", updated_at: now })
      .eq("id", taskId)

    if (updateError) throw updateError

    // Log to task_history
    const { error: historyError } = await supabaseAdmin
      .from("task_history")
      .insert({
        task_id: taskId,
        action: "status_changed",
        changed_by: "clawdbot",
        changes: {
          from: "queued",
          to: "in_progress",
          timestamp: now,
        },
        created_at: now,
      })

    // task_history insert failure is non-fatal — log but continue
    if (historyError) {
      console.warn("task_history insert failed:", historyError.message)
    }

    // Write pending task file for Clawdbot to pick up
    const pendingTask = {
      taskId: task.id,
      title: task.title,
      description: task.description,
      priority: task.priority,
      momentum_score: task.momentum_score,
      assigned_at: now,
    }

    try {
      await fs.writeFile(
        PENDING_TASK_PATH,
        JSON.stringify(pendingTask, null, 2),
        "utf-8"
      )
    } catch (fsErr) {
      // Non-fatal on Vercel (serverless can't write to local FS), but works locally
      console.warn("Could not write pending-task.json:", fsErr)
    }

    return NextResponse.json({
      success: true,
      task: { ...task, status: "in_progress", updated_at: now },
      pendingTaskWritten: true,
    })
  } catch (err) {
    const message = err instanceof Error ? err.message : "Unknown error"
    return NextResponse.json({ error: message }, { status: 500 })
  }
}
