import { getThemePerformance, getCapitalAllocationHistory } from "@/lib/supabase/trading"
import ThemeCard from "../components/ThemeCard"
import { Card } from "@/components/ui/card"

export default async function ThemesPage() {
  // Fetch theme performance data
  const themes = await getThemePerformance()
  const allocationHistory = await getCapitalAllocationHistory(12)

  // Theme icons
  const themeIcons: Record<string, string> = {
    geopolitical: "🌍",
    us_politics: "🇺🇸",
    crypto: "₿",
    weather: "🌦️",
  }

  // Prepare pie chart data (capital distribution)
  const totalCapital = themes.reduce((sum, t) => sum + t.current_capital, 0)
  const pieData = themes.map((theme) => ({
    name: theme.theme,
    value: theme.current_capital,
    percentage: (theme.current_capital / totalCapital) * 100,
  }))

  // Prepare area chart data (capital allocation over time)
  // Group by week_start
  const weekMap = new Map<string, Record<string, number>>()
  allocationHistory.forEach((point) => {
    if (!weekMap.has(point.week_start)) {
      weekMap.set(point.week_start, {})
    }
    weekMap.get(point.week_start)![point.theme] = point.capital
  })

  const weeks = Array.from(weekMap.keys()).sort()
  const areaChartData = weeks.map((week) => ({
    week,
    ...weekMap.get(week),
  }))

  return (
    <div className="p-8 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">🎯 Theme Performance</h1>
        <p className="text-muted-foreground mt-1">
          Track performance across 4 investment themes
        </p>
      </div>

      {/* Theme Cards - 4 Column Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {themes.map((theme) => (
          <ThemeCard
            key={theme.theme}
            name={theme.theme}
            icon={themeIcons[theme.theme] || "📊"}
            currentCapital={theme.current_capital}
            pnl7d={theme.pnl_7d}
            pnl30d={theme.pnl_30d}
            winRate={theme.win_rate}
            agentCount={theme.agent_count}
            status={theme.status}
          />
        ))}
      </div>

      {/* Capital Allocation - Pie Chart */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4">💰 Current Capital Allocation</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Simple visual representation */}
          <div className="space-y-3">
            {pieData.map((data, index) => (
              <div key={data.name}>
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <span className="text-xl">{themeIcons[data.name]}</span>
                    <span className="text-sm font-medium capitalize">
                      {data.name.split("_").join(" ")}
                    </span>
                  </div>
                  <span className="text-sm font-semibold">
                    ${data.value.toLocaleString()} ({data.percentage.toFixed(1)}%)
                  </span>
                </div>
                <div className="w-full h-3 bg-secondary rounded-full overflow-hidden">
                  <div
                    className="h-full"
                    style={{
                      width: `${data.percentage}%`,
                      background: `hsl(${index * 90}, 70%, 50%)`,
                    }}
                  />
                </div>
              </div>
            ))}
          </div>

          {/* Summary Stats */}
          <div className="space-y-4">
            <div className="p-4 rounded-lg bg-secondary/50">
              <p className="text-xs text-muted-foreground mb-1">Total Portfolio Value</p>
              <p className="text-3xl font-bold">${totalCapital.toLocaleString()}</p>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="p-4 rounded-lg bg-secondary/50">
                <p className="text-xs text-muted-foreground mb-1">Active Themes</p>
                <p className="text-2xl font-bold">
                  {themes.filter((t) => t.status === "ACTIVE").length}
                </p>
              </div>
              <div className="p-4 rounded-lg bg-secondary/50">
                <p className="text-xs text-muted-foreground mb-1">Total Agents</p>
                <p className="text-2xl font-bold">
                  {themes.reduce((sum, t) => sum + t.agent_count, 0)}
                </p>
              </div>
            </div>
          </div>
        </div>
      </Card>

      {/* Historical Allocation - Area Chart */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4">📈 Capital Flow Over Time (12 Weeks)</h3>
        {areaChartData.length > 0 ? (
          <div className="space-y-4">
            {/* Simple stacked bar chart representation */}
            <div className="h-64 flex items-end gap-2">
              {areaChartData.slice(-12).map((week, i) => {
                const weekData = week as any
                const weekTotal =
                  (weekData.geopolitical || 0) +
                  (weekData.us_politics || 0) +
                  (weekData.crypto || 0) +
                  (weekData.weather || 0)

                return (
                  <div key={i} className="flex-1 flex flex-col justify-end">
                    {/* Stacked bars */}
                    <div className="w-full flex flex-col-reverse gap-0.5">
                      {["geopolitical", "us_politics", "crypto", "weather"].map((theme, idx) => {
                        const value = weekData[theme] || 0
                        const height = (value / weekTotal) * 100

                        return (
                          <div
                            key={theme}
                            className="w-full rounded-sm"
                            style={{
                              height: `${height}%`,
                              background: `hsl(${idx * 90}, 70%, 50%)`,
                            }}
                            title={`${theme}: $${value.toLocaleString()}`}
                          />
                        )
                      })}
                    </div>
                    {/* Week label */}
                    <p className="text-[10px] text-muted-foreground text-center mt-2">
                      {new Date(weekData.week).toLocaleDateString("en-US", {
                        month: "short",
                        day: "numeric",
                      })}
                    </p>
                  </div>
                )
              })}
            </div>

            {/* Legend */}
            <div className="flex items-center justify-center gap-6">
              {["geopolitical", "us_politics", "crypto", "weather"].map((theme, idx) => (
                <div key={theme} className="flex items-center gap-2">
                  <div
                    className="w-3 h-3 rounded-sm"
                    style={{ background: `hsl(${idx * 90}, 70%, 50%)` }}
                  />
                  <span className="text-xs capitalize">
                    {theme.split("_").join(" ")}
                  </span>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <p className="text-center text-muted-foreground py-8">
            No allocation history available yet
          </p>
        )}
      </Card>

      {/* Performance Summary Table */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4">📊 Theme Performance Summary</h3>
        <div className="rounded-md border">
          <table className="w-full">
            <thead className="bg-secondary/50">
              <tr className="border-b">
                <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground">
                  Theme
                </th>
                <th className="px-4 py-3 text-right text-xs font-medium text-muted-foreground">
                  Capital
                </th>
                <th className="px-4 py-3 text-right text-xs font-medium text-muted-foreground">
                  7d P&L
                </th>
                <th className="px-4 py-3 text-right text-xs font-medium text-muted-foreground">
                  30d P&L
                </th>
                <th className="px-4 py-3 text-right text-xs font-medium text-muted-foreground">
                  Win Rate
                </th>
                <th className="px-4 py-3 text-right text-xs font-medium text-muted-foreground">
                  Trades
                </th>
                <th className="px-4 py-3 text-center text-xs font-medium text-muted-foreground">
                  Status
                </th>
              </tr>
            </thead>
            <tbody>
              {themes.map((theme) => (
                <tr key={theme.theme} className="border-b hover:bg-secondary/30 transition-colors">
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <span className="text-xl">{themeIcons[theme.theme]}</span>
                      <span className="text-sm font-medium capitalize">
                        {theme.theme.split("_").join(" ")}
                      </span>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-right text-sm font-mono">
                    ${theme.current_capital.toLocaleString()}
                  </td>
                  <td
                    className={`px-4 py-3 text-right text-sm font-semibold ${
                      theme.pnl_7d >= 0 ? "text-green-500" : "text-red-500"
                    }`}
                  >
                    ${theme.pnl_7d >= 0 ? "+" : ""}
                    {theme.pnl_7d.toFixed(2)}
                  </td>
                  <td
                    className={`px-4 py-3 text-right text-sm font-semibold ${
                      theme.pnl_30d >= 0 ? "text-green-500" : "text-red-500"
                    }`}
                  >
                    ${theme.pnl_30d >= 0 ? "+" : ""}
                    {theme.pnl_30d.toFixed(2)}
                  </td>
                  <td className="px-4 py-3 text-right text-sm font-semibold">
                    {(theme.win_rate * 100).toFixed(1)}%
                  </td>
                  <td className="px-4 py-3 text-right text-sm text-muted-foreground">
                    {theme.total_trades}
                  </td>
                  <td className="px-4 py-3 text-center">
                    <span
                      className={`px-2 py-1 rounded text-xs font-medium ${
                        theme.status === "ACTIVE"
                          ? "bg-green-500/10 text-green-500"
                          : theme.status === "PROBATION"
                          ? "bg-yellow-500/10 text-yellow-500"
                          : "bg-red-500/10 text-red-500"
                      }`}
                    >
                      {theme.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  )
}
