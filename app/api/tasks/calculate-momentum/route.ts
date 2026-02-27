import { NextResponse } from "next/server"
import { getSupabaseAdmin } from "@/lib/supabaseAdmin"

const STOP_WORDS = new Set([
  "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
  "of", "with", "by", "from", "is", "are", "was", "were", "be", "been",
  "being", "have", "has", "had", "do", "does", "did", "will", "would",
  "could", "should", "may", "might", "shall", "can", "need", "dare",
  "ought", "used", "it", "its", "this", "that", "these", "those", "as",
  "into", "through", "up", "out", "about", "after", "before", "between",
  "so", "if", "then", "than", "not", "no", "nor", "each", "every",
  "all", "both", "few", "more", "most", "other", "some", "such", "any",
])

function extractKeywords(text: string): Set<string> {
  return new Set(
    text
      .toLowerCase()
      .replace(/[^a-z0-9\s]/g, " ")
      .split(/\s+/)
      .filter((w) => w.length > 2 && !STOP_WORDS.has(w))
  )
}

function calculateScore(
  taskKeywords: Set<string>,
  completedKeywords: Set<string>
): number {
  if (completedKeywords.size === 0) return 0

  let matches = 0
  for (const kw of taskKeywords) {
    if (completedKeywords.has(kw)) matches++
  }

  const totalUnique = new Set([...taskKeywords, ...completedKeywords]).size
  if (totalUnique === 0) return 0

  return Math.round((matches / totalUnique) * 100)
}

export async function POST() {
  try {
    const supabaseAdmin = getSupabaseAdmin()
    // Fetch all queued tasks
    const { data: queuedTasks, error: queuedError } = await supabaseAdmin
      .from("tasks")
      .select("*")
      .eq("status", "queued")

    if (queuedError) throw queuedError

    // Fetch last 10 done tasks
    const { data: doneTasks, error: doneError } = await supabaseAdmin
      .from("tasks")
      .select("*")
      .eq("status", "done")
      .order("updated_at", { ascending: false })
      .limit(10)

    if (doneError) throw doneError

    if (!queuedTasks || queuedTasks.length === 0) {
      return NextResponse.json({ updated: [], message: "No queued tasks" })
    }

    // Build keyword set from all done tasks combined
    const completedKeywords = new Set<string>()
    for (const task of doneTasks ?? []) {
      const text = `${task.title ?? ""} ${task.description ?? ""}`
      for (const kw of extractKeywords(text)) {
        completedKeywords.add(kw)
      }
    }

    const noDoneTasksYet = (doneTasks?.length ?? 0) === 0

    // Calculate momentum for each queued task
    const updates: { id: string; momentum_score: number }[] = []

    for (const task of queuedTasks) {
      let score: number

      if (noDoneTasksYet) {
        // Fallback: priority-based score
        if (task.priority === "high") score = 80
        else if (task.priority === "medium") score = 50
        else score = 20
      } else {
        const taskKeywords = extractKeywords(
          `${task.title ?? ""} ${task.description ?? ""}`
        )
        score = calculateScore(taskKeywords, completedKeywords)
      }

      updates.push({ id: task.id, momentum_score: score })
    }

    // Write scores back to Supabase
    const results: Array<{ id: string; momentum_score: number; error?: string }> = []

    for (const update of updates) {
      const { error } = await supabaseAdmin
        .from("tasks")
        .update({
          momentum_score: update.momentum_score,
          updated_at: new Date().toISOString(),
        })
        .eq("id", update.id)

      results.push({
        id: update.id,
        momentum_score: update.momentum_score,
        ...(error ? { error: error.message } : {}),
      })
    }

    return NextResponse.json({
      updated: results,
      count: results.length,
    })
  } catch (err) {
    const message = err instanceof Error ? err.message : "Unknown error"
    return NextResponse.json({ error: message }, { status: 500 })
  }
}
