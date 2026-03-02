import { getAgentPerformance } from "@/lib/supabase/trading"
import AgentLeaderboard from "../components/AgentLeaderboard"
import { Card } from "@/components/ui/card"

export default async function AgentsPage() {
  // Fetch agent performance data
  const agents = await getAgentPerformance()

  // Calculate summary stats
  const totalTrades = agents.reduce((sum, a) => sum + a.total_trades, 0)
  const avgWinRate =
    agents.length > 0
      ? agents.reduce((sum, a) => sum + a.win_rate, 0) / agents.length
      : 0
  const total7dPnl = agents.reduce((sum, a) => sum + a.pnl_7d, 0)
  const topPerformer = agents.length > 0 ? agents[0] : null

  // Format agent name for display
  const formatAgentName = (agentId: string) => {
    return agentId
      .split("_")
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(" ")
  }

  return (
    <div className="p-8 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">🤖 Agent Leaderboard</h1>
        <p className="text-muted-foreground mt-1">
          Performance rankings for all institutional agents
        </p>
      </div>

      {/* Summary Stats - 4 Column Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="p-6">
          <div className="space-y-2">
            <p className="text-xs text-muted-foreground">Total Agents</p>
            <p className="text-3xl font-bold">{agents.length}</p>
            <p className="text-xs text-muted-foreground">
              Across 4 themes
            </p>
          </div>
        </Card>

        <Card className="p-6">
          <div className="space-y-2">
            <p className="text-xs text-muted-foreground">Avg Win Rate</p>
            <p className="text-3xl font-bold">{(avgWinRate * 100).toFixed(1)}%</p>
            <p className="text-xs text-muted-foreground">
              System-wide performance
            </p>
          </div>
        </Card>

        <Card className="p-6">
          <div className="space-y-2">
            <p className="text-xs text-muted-foreground">Total Trades (7d)</p>
            <p className="text-3xl font-bold">{totalTrades}</p>
            <p className="text-xs text-muted-foreground">
              Last 7 days
            </p>
          </div>
        </Card>

        <Card className="p-6">
          <div className="space-y-2">
            <p className="text-xs text-muted-foreground">7d P&L</p>
            <p
              className={`text-3xl font-bold ${
                total7dPnl >= 0 ? "text-green-500" : "text-red-500"
              }`}
            >
              ${total7dPnl >= 0 ? "+" : ""}
              {total7dPnl.toFixed(2)}
            </p>
            <p className="text-xs text-muted-foreground">
              All agents combined
            </p>
          </div>
        </Card>
      </div>

      {/* Top Performer Highlight */}
      {topPerformer && (
        <Card className="p-6 bg-gradient-to-r from-yellow-500/10 to-transparent border-yellow-500/20">
          <div className="flex items-center gap-4">
            <div className="text-5xl">🏆</div>
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-yellow-500 mb-1">
                Top Performer (7d)
              </h3>
              <p className="text-2xl font-bold mb-2">
                {formatAgentName(topPerformer.agent_id)}
              </p>
              <div className="flex items-center gap-6 text-sm">
                <div>
                  <span className="text-muted-foreground">Win Rate: </span>
                  <span className="font-semibold">
                    {(topPerformer.win_rate * 100).toFixed(1)}%
                  </span>
                </div>
                <div>
                  <span className="text-muted-foreground">7d P&L: </span>
                  <span
                    className={`font-semibold ${
                      topPerformer.pnl_7d >= 0 ? "text-green-500" : "text-red-500"
                    }`}
                  >
                    ${topPerformer.pnl_7d >= 0 ? "+" : ""}
                    {topPerformer.pnl_7d.toFixed(2)}
                  </span>
                </div>
                <div>
                  <span className="text-muted-foreground">Trades: </span>
                  <span className="font-semibold">{topPerformer.total_trades}</span>
                </div>
                <div>
                  <span className="text-muted-foreground">Theme: </span>
                  <span className="font-semibold capitalize">
                    {topPerformer.theme.split("_").join(" ")}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </Card>
      )}

      {/* Agent Leaderboard Table */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4">🏅 Performance Rankings</h3>
        <AgentLeaderboard agents={agents} />
      </Card>

      {/* Win Rate Distribution */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4">📊 Win Rate Distribution</h3>
        <div className="space-y-3">
          {/* Buckets: 0-25%, 26-50%, 51-75%, 76-100% */}
          {[
            { label: "76-100%", min: 0.76, color: "bg-green-500" },
            { label: "51-75%", min: 0.51, color: "bg-blue-500" },
            { label: "26-50%", min: 0.26, color: "bg-yellow-500" },
            { label: "0-25%", min: 0, color: "bg-red-500" },
          ].map((bucket) => {
            const count = agents.filter(
              (a) => a.win_rate >= bucket.min && a.win_rate < bucket.min + 0.25
            ).length
            const percentage = agents.length > 0 ? (count / agents.length) * 100 : 0

            return (
              <div key={bucket.label}>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium">{bucket.label}</span>
                  <span className="text-sm text-muted-foreground">
                    {count} agents ({percentage.toFixed(0)}%)
                  </span>
                </div>
                <div className="w-full h-3 bg-secondary rounded-full overflow-hidden">
                  <div className={`h-full ${bucket.color}`} style={{ width: `${percentage}%` }} />
                </div>
              </div>
            )
          })}
        </div>
      </Card>

      {/* Theme Breakdown */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4">🎯 Performance by Theme</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {["geopolitical", "us_politics", "crypto", "weather"].map((theme) => {
            const themeAgents = agents.filter((a) => a.theme === theme)
            const themeWinRate =
              themeAgents.length > 0
                ? themeAgents.reduce((sum, a) => sum + a.win_rate, 0) / themeAgents.length
                : 0
            const themePnl = themeAgents.reduce((sum, a) => sum + a.pnl_7d, 0)

            const themeIcons: Record<string, string> = {
              geopolitical: "🌍",
              us_politics: "🇺🇸",
              crypto: "₿",
              weather: "🌦️",
            }

            return (
              <div key={theme} className="p-4 rounded-lg bg-secondary/50">
                <div className="flex items-center gap-2 mb-3">
                  <span className="text-2xl">{themeIcons[theme]}</span>
                  <span className="text-sm font-medium capitalize">
                    {theme.split("_").join(" ")}
                  </span>
                </div>
                <div className="space-y-2">
                  <div>
                    <p className="text-xs text-muted-foreground">Agents</p>
                    <p className="text-xl font-bold">{themeAgents.length}</p>
                  </div>
                  <div>
                    <p className="text-xs text-muted-foreground">Avg Win Rate</p>
                    <p className="text-lg font-semibold">{(themeWinRate * 100).toFixed(1)}%</p>
                  </div>
                  <div>
                    <p className="text-xs text-muted-foreground">7d P&L</p>
                    <p
                      className={`text-lg font-semibold ${
                        themePnl >= 0 ? "text-green-500" : "text-red-500"
                      }`}
                    >
                      ${themePnl >= 0 ? "+" : ""}
                      {themePnl.toFixed(2)}
                    </p>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      </Card>
    </div>
  )
}
