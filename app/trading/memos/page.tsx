import { getMemos } from "@/lib/supabase/trading"
import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import Link from "next/link"

export default async function MemosPage() {
  // Fetch last 30 memos
  const memos = await getMemos(30)

  return (
    <div className="p-8 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">IC Memos</h1>
        <p className="text-muted-foreground mt-1">
          Daily investment committee reports and analysis
        </p>
      </div>

      {/* Memos Grid */}
      {memos.length === 0 ? (
        <Card className="p-12 text-center">
          <p className="text-muted-foreground">No IC memos found</p>
          <p className="text-sm text-muted-foreground mt-2">
            Memos are generated daily by the trading bot
          </p>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {memos.map((memo, index) => {
            const isLatest = index === 0
            const memoDate = new Date(memo.date)

            return (
              <Link
                key={memo.id}
                href={`/trading/memos/${memo.date}`}
                className="block"
              >
                <Card className="p-6 hover:border-[#0077ff] transition-colors cursor-pointer h-full">
                  <div className="space-y-3">
                    {/* Date + Latest Badge */}
                    <div className="flex items-center justify-between">
                      <h3 className="text-lg font-semibold">
                        {memoDate.toLocaleDateString("en-US", {
                          month: "short",
                          day: "numeric",
                          year: "numeric",
                        })}
                      </h3>
                      {isLatest && (
                        <Badge variant="success">Latest</Badge>
                      )}
                    </div>

                    {/* Summary Stats */}
                    <div className="grid grid-cols-2 gap-3 text-sm">
                      <div>
                        <p className="text-xs text-muted-foreground">Trades</p>
                        <p className="font-mono font-semibold">
                          {memo.trades_count}
                        </p>
                      </div>
                      <div>
                        <p className="text-xs text-muted-foreground">Win Rate</p>
                        <p className="font-mono font-semibold">
                          {memo.win_rate !== null
                            ? `${memo.win_rate.toFixed(1)}%`
                            : "—"}
                        </p>
                      </div>
                      <div className="col-span-2">
                        <p className="text-xs text-muted-foreground">
                          Daily Return
                        </p>
                        <p
                          className={`font-mono font-semibold ${
                            (memo.daily_return ?? 0) >= 0
                              ? "text-green-500"
                              : "text-red-500"
                          }`}
                        >
                          {memo.daily_return !== null
                            ? `${memo.daily_return >= 0 ? "+" : ""}${memo.daily_return.toFixed(2)}%`
                            : "—"}
                        </p>
                      </div>
                    </div>

                    {/* Preview */}
                    <div className="pt-2 border-t border-[#1e2d3d]">
                      <p className="text-xs text-muted-foreground line-clamp-2">
                        {memo.memo_text.split("\n")[0].replace(/^#+ /, "")}
                      </p>
                    </div>
                  </div>
                </Card>
              </Link>
            )
          })}
        </div>
      )}
    </div>
  )
}
