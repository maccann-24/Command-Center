import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import Link from "next/link"

type ThemeCardProps = {
  name: string
  icon: string
  currentCapital: number
  pnl7d: number
  pnl30d: number
  winRate: number
  agentCount: number
  status: "ACTIVE" | "PROBATION" | "PAUSED"
  sparklineData?: number[] // Optional sparkline data
}

export default function ThemeCard({
  name,
  icon,
  currentCapital,
  pnl7d,
  pnl30d,
  winRate,
  agentCount,
  status,
  sparklineData = [],
}: ThemeCardProps) {
  // Status badge styling
  const statusColors = {
    ACTIVE: "bg-green-500/10 text-green-500 border-green-500/20",
    PROBATION: "bg-yellow-500/10 text-yellow-500 border-yellow-500/20",
    PAUSED: "bg-red-500/10 text-red-500 border-red-500/20",
  }

  // Format theme name for display
  const displayName = name
    .split("_")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ")

  return (
    <Link href={`/trading/themes/${name}`}>
      <Card className="p-6 hover:border-blue-500/50 transition-all cursor-pointer group">
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="text-3xl">{icon}</div>
            <div>
              <h3 className="font-semibold text-lg group-hover:text-blue-500 transition-colors">
                {displayName}
              </h3>
              <p className="text-xs text-muted-foreground">
                {agentCount} agents
              </p>
            </div>
          </div>
          <Badge className={statusColors[status]}>
            {status}
          </Badge>
        </div>

        {/* Capital Allocation */}
        <div className="mb-4">
          <p className="text-xs text-muted-foreground mb-1">Current Capital</p>
          <p className="text-2xl font-bold">${currentCapital.toLocaleString()}</p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div>
            <p className="text-xs text-muted-foreground mb-1">7d P&L</p>
            <p
              className={`text-lg font-semibold ${
                pnl7d >= 0 ? "text-green-500" : "text-red-500"
              }`}
            >
              ${pnl7d >= 0 ? "+" : ""}
              {pnl7d.toFixed(2)}
            </p>
          </div>
          <div>
            <p className="text-xs text-muted-foreground mb-1">30d P&L</p>
            <p
              className={`text-lg font-semibold ${
                pnl30d >= 0 ? "text-green-500" : "text-red-500"
              }`}
            >
              ${pnl30d >= 0 ? "+" : ""}
              {pnl30d.toFixed(2)}
            </p>
          </div>
        </div>

        {/* Win Rate */}
        <div className="mb-4">
          <div className="flex items-center justify-between mb-2">
            <p className="text-xs text-muted-foreground">Win Rate</p>
            <p className="text-sm font-semibold">
              {(winRate * 100).toFixed(1)}%
            </p>
          </div>
          <div className="w-full h-2 bg-secondary rounded-full overflow-hidden">
            <div
              className="h-full bg-blue-500"
              style={{ width: `${winRate * 100}%` }}
            />
          </div>
        </div>

        {/* Mini Sparkline (if data available) */}
        {sparklineData.length > 0 && (
          <div className="h-12 flex items-end gap-0.5">
            {sparklineData.map((value, i) => {
              const max = Math.max(...sparklineData)
              const min = Math.min(...sparklineData)
              const range = max - min || 1
              const height = ((value - min) / range) * 100

              return (
                <div
                  key={i}
                  className="flex-1 bg-blue-500/20 rounded-sm"
                  style={{ height: `${height}%` }}
                />
              )
            })}
          </div>
        )}
      </Card>
    </Link>
  )
}
