import { getPortfolio, getPortfolioHistory } from "@/lib/supabase/trading"
import PortfolioCard from "./components/PortfolioCard"
import Sparkline from "./components/Sparkline"
import BotStatusCard from "./components/BotStatusCard"
import { Card } from "@/components/ui/card"

export default async function TradingPage() {
  // Fetch portfolio data and history
  const portfolio = await getPortfolio()
  const history = await getPortfolioHistory(7)

  // Format values for display
  const cash = portfolio?.cash ?? 0
  const totalValue = portfolio?.total_value ?? 0
  const deployedPct = portfolio?.deployed_pct ?? 0
  const dailyPnl = portfolio?.daily_pnl ?? 0
  const allTimePnl = portfolio?.all_time_pnl ?? 0

  return (
    <div className="p-8 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">💰 Trading Dashboard</h1>
        <p className="text-muted-foreground mt-1">
          Real-time portfolio tracking and bot status
        </p>
      </div>

      {/* Bot Status Card */}
      <BotStatusCard />

      {/* Portfolio Stats - 2x2 Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <PortfolioCard
          title="Cash"
          value={cash}
          format="currency"
          icon="💵"
        />
        <PortfolioCard
          title="Total Value"
          value={totalValue}
          format="currency"
          icon="💎"
        />
        <PortfolioCard
          title="Deployed"
          value={deployedPct}
          format="percentage"
          icon="📊"
        />
        <PortfolioCard
          title="Daily P&L"
          value={dailyPnl}
          format="pnl"
          icon="📈"
        />
      </div>

      {/* Sparkline Chart */}
      <Card className="p-6">
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold">Portfolio Value (7 Days)</h3>
              <p className="text-sm text-muted-foreground">
                All-time P&L: {" "}
                <span
                  className={
                    allTimePnl >= 0
                      ? "text-green-500 font-semibold"
                      : "text-red-500 font-semibold"
                  }
                >
                  ${allTimePnl.toFixed(2)}
                </span>
              </p>
            </div>
          </div>
          <Sparkline data={history} />
        </div>
      </Card>

      {/* Quick Actions / Info */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="p-6">
          <h4 className="font-semibold mb-2">📍 Quick Links</h4>
          <div className="space-y-2 text-sm">
            <a href="/trading/markets" className="block text-blue-500 hover:underline">
              → View Markets
            </a>
            <a href="/trading/theses" className="block text-blue-500 hover:underline">
              → Active Theses
            </a>
            <a href="/trading/positions" className="block text-blue-500 hover:underline">
              → Open Positions
            </a>
          </div>
        </Card>

        <Card className="p-6">
          <h4 className="font-semibold mb-2">⚙️ System Info</h4>
          <div className="space-y-1 text-sm text-muted-foreground">
            <p>Mode: <span className="font-mono">paper</span></p>
            <p>Risk Limit: <span className="font-mono">60% deployed</span></p>
            <p>Stop Loss: <span className="font-mono">15%</span></p>
          </div>
        </Card>

        <Card className="p-6">
          <h4 className="font-semibold mb-2">📝 Latest Activity</h4>
          <div className="space-y-1 text-sm text-muted-foreground">
            <p>Last cycle: <span className="font-mono">2m ago</span></p>
            <p>Active theses: <span className="font-mono">12</span></p>
            <p>Open positions: <span className="font-mono">3</span></p>
          </div>
        </Card>
      </div>
    </div>
  )
}
