import { getMarkets } from "@/lib/supabase/trading"
import MarketTable from "../components/MarketTable"

export default async function MarketsPage() {
  // Fetch all markets (filtering will be done client-side)
  const markets = await getMarkets({ limit: 500 })

  return (
    <div className="p-8 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">Markets</h1>
        <p className="text-muted-foreground mt-1">
          Browse and filter active prediction markets
        </p>
      </div>

      {/* Market Table */}
      <MarketTable markets={markets} />
    </div>
  )
}
