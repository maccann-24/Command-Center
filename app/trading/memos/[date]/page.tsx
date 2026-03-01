import { getMemoByDate, getMemos } from "@/lib/supabase/trading"
import MemoViewer from "../../components/MemoViewer"
import { notFound } from "next/navigation"
import Link from "next/link"
import { ChevronLeft, ChevronRight } from "lucide-react"

type Props = {
  params: Promise<{ date: string }>
}

export default async function MemoDetailPage({ params }: Props) {
  const { date } = await params
  const memo = await getMemoByDate(date)

  if (!memo) {
    notFound()
  }

  // Get previous and next memos for navigation
  const allMemos = await getMemos(90) // Get more for navigation
  const currentIndex = allMemos.findIndex((m) => m.date === date)
  const prevMemo = currentIndex < allMemos.length - 1 ? allMemos[currentIndex + 1] : null
  const nextMemo = currentIndex > 0 ? allMemos[currentIndex - 1] : null

  return (
    <div className="p-8 space-y-6 max-w-5xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <Link
          href="/trading/memos"
          className="text-sm text-[#0077ff] hover:underline flex items-center gap-1"
        >
          <ChevronLeft className="w-4 h-4" />
          Back to Memos
        </Link>
        <div className="flex items-center gap-2">
          {prevMemo && (
            <Link
              href={`/trading/memos/${prevMemo.date}`}
              className="px-3 py-2 text-sm border border-[#1e2d3d] rounded hover:bg-[#0d1117] flex items-center gap-1"
              title={`Previous: ${prevMemo.date}`}
            >
              <ChevronLeft className="w-4 h-4" />
              Previous
            </Link>
          )}
          {nextMemo && (
            <Link
              href={`/trading/memos/${nextMemo.date}`}
              className="px-3 py-2 text-sm border border-[#1e2d3d] rounded hover:bg-[#0d1117] flex items-center gap-1"
              title={`Next: ${nextMemo.date}`}
            >
              Next
              <ChevronRight className="w-4 h-4" />
            </Link>
          )}
        </div>
      </div>

      {/* Memo Viewer */}
      <MemoViewer memo={memo} />
    </div>
  )
}
