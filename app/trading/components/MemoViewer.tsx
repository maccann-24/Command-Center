"use client"

import { Card } from "@/components/ui/card"
import type { ICMemo } from "@/lib/supabase/trading"

type MemoViewerProps = {
  memo: ICMemo
}

export default function MemoViewer({ memo }: MemoViewerProps) {
  const memoDate = new Date(memo.date)

  // Simple markdown to HTML conversion
  const renderMarkdown = (text: string): string => {
    return text
      // Headers
      .replace(/^### (.*$)/gim, '<h3 class="text-lg font-semibold mt-6 mb-3">$1</h3>')
      .replace(/^## (.*$)/gim, '<h2 class="text-xl font-semibold mt-8 mb-4">$1</h2>')
      .replace(/^# (.*$)/gim, '<h1 class="text-2xl font-bold mt-10 mb-6">$1</h1>')
      // Bold
      .replace(/\*\*(.*?)\*\*/gim, '<strong class="font-semibold">$1</strong>')
      // Italic
      .replace(/\*(.*?)\*/gim, '<em class="italic">$1</em>')
      // Code blocks
      .replace(/```(\w+)?\n([\s\S]*?)```/gim, '<pre class="bg-[#0d1117] p-4 rounded my-4 overflow-x-auto"><code class="text-sm font-mono">$2</code></pre>')
      // Inline code
      .replace(/`([^`]+)`/gim, '<code class="bg-[#0d1117] px-1.5 py-0.5 rounded text-sm font-mono">$1</code>')
      // Links
      .replace(/\[([^\]]+)\]\(([^)]+)\)/gim, '<a href="$2" class="text-[#0077ff] hover:underline" target="_blank" rel="noopener noreferrer">$1</a>')
      // Unordered lists
      .replace(/^\- (.*$)/gim, '<li class="ml-4">$1</li>')
      .replace(/(<li.*<\/li>)/gim, '<ul class="list-disc list-inside my-2">$1</ul>')
      // Ordered lists
      .replace(/^\d+\. (.*$)/gim, '<li class="ml-4">$1</li>')
      // Horizontal rule
      .replace(/^---$/gim, '<hr class="my-6 border-[#1e2d3d]" />')
      // Line breaks
      .replace(/\n\n/gim, '</p><p class="mb-4">')
      .replace(/\n/gim, '<br />')
  }

  const htmlContent = `<div class="prose prose-invert max-w-none"><p class="mb-4">${renderMarkdown(memo.memo_text)}</p></div>`

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">
          IC Memo - {memoDate.toLocaleDateString("en-US", {
            month: "long",
            day: "numeric",
            year: "numeric",
          })}
        </h1>
        <p className="text-sm text-muted-foreground mt-2">
          Generated {new Date(memo.created_at).toLocaleString()}
        </p>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="p-4">
          <div className="space-y-1">
            <p className="text-xs font-medium text-muted-foreground">Trades Executed</p>
            <p className="text-2xl font-bold">{memo.trades_count}</p>
          </div>
        </Card>
        <Card className="p-4">
          <div className="space-y-1">
            <p className="text-xs font-medium text-muted-foreground">Win Rate</p>
            <p className="text-2xl font-bold">
              {memo.win_rate !== null ? `${memo.win_rate.toFixed(1)}%` : "—"}
            </p>
          </div>
        </Card>
        <Card className="p-4">
          <div className="space-y-1">
            <p className="text-xs font-medium text-muted-foreground">Daily Return</p>
            <p
              className={`text-2xl font-bold ${
                (memo.daily_return ?? 0) >= 0 ? "text-green-500" : "text-red-500"
              }`}
            >
              {memo.daily_return !== null
                ? `${memo.daily_return >= 0 ? "+" : ""}${memo.daily_return.toFixed(2)}%`
                : "—"}
            </p>
          </div>
        </Card>
      </div>

      {/* Memo Content */}
      <Card className="p-8">
        <div
          className="text-sm leading-relaxed"
          dangerouslySetInnerHTML={{ __html: htmlContent }}
        />
      </Card>

      {/* Portfolio Summary (if available) */}
      {memo.portfolio_summary && (
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">Portfolio Snapshot</h3>
          <pre className="bg-[#0d1117] p-4 rounded overflow-x-auto text-xs font-mono">
            {JSON.stringify(memo.portfolio_summary, null, 2)}
          </pre>
        </Card>
      )}
    </div>
  )
}
