import { getPositions, getPositionStats } from "@/lib/supabase/trading"
import PositionTable from "../components/PositionTable"
import { Card } from "@/components/ui/card"

export default async function PositionsPage() {
  // Fetch all positions and stats
  const positions = await getPositions({ limit: 500 })
  const stats = await getPositionStats()

  return (
    <div className="p-8 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">Positions</h1>
        <p className="text-muted-foreground mt-1">
          Track open and closed positions with P&L
        </p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="p-4">
          <div className="space-y-1">
            <p className="text-xs font-medium text-muted-foreground">Total Open P&L</p>
            <p
              className={`text-2xl font-bold ${
                (stats?.total_open_pnl ?? 0) >= 0
                  ? "text-green-500"
                  : "text-red-500"
              }`}
            >
              ${(stats?.total_open_pnl ?? 0).toFixed(2)}
            </p>
          </div>
        </Card>

        <Card className="p-4">
          <div className="space-y-1">
            <p className="text-xs font-medium text-muted-foreground">Win Rate</p>
            <p className="text-2xl font-bold">
              {stats?.win_rate !== null && stats?.win_rate !== undefined
                ? `${stats.win_rate.toFixed(1)}%`
                : "—"}
            </p>
          </div>
        </Card>

        <Card className="p-4">
          <div className="space-y-1">
            <p className="text-xs font-medium text-muted-foreground">Largest Win</p>
            <p className="text-2xl font-bold text-green-500">
              ${(stats?.largest_win ?? 0).toFixed(2)}
            </p>
          </div>
        </Card>

        <Card className="p-4">
          <div className="space-y-1">
            <p className="text-xs font-medium text-muted-foreground">Largest Loss</p>
            <p className="text-2xl font-bold text-red-500">
              ${(stats?.largest_loss ?? 0).toFixed(2)}
            </p>
          </div>
        </Card>
      </div>

      {/* Position Table */}
      <PositionTable positions={positions} />
    </div>
  )
}
