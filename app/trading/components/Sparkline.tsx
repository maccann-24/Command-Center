"use client"

import { useMemo } from "react"
import { LineChart, Line, ResponsiveContainer, Tooltip } from "recharts"
import type { PortfolioHistoryPoint } from "@/lib/supabase/trading"

type SparklineProps = {
  data: PortfolioHistoryPoint[]
}

export default function Sparkline({ data }: SparklineProps) {
  // Determine trend direction (up/down) for color
  const trend = useMemo(() => {
    if (data.length < 2) return "neutral"
    const first = data[0]?.total_value ?? 0
    const last = data[data.length - 1]?.total_value ?? 0
    return last >= first ? "up" : "down"
  }, [data])

  // Format data for recharts
  const chartData = useMemo(() => {
    return data.map((point) => ({
      timestamp: new Date(point.ts).toLocaleDateString("en-US", {
        month: "short",
        day: "numeric",
      }),
      value: point.total_value,
    }))
  }, [data])

  // Handle empty data
  if (data.length === 0) {
    return (
      <div className="h-[200px] flex items-center justify-center text-muted-foreground">
        No historical data available
      </div>
    )
  }

  const lineColor = trend === "up" ? "#00d084" : "#ef4444"

  return (
    <div className="h-[200px]">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData}>
          <defs>
            <linearGradient id="sparklineGradient" x1="0" y1="0" x2="0" y2="1">
              <stop
                offset="5%"
                stopColor={lineColor}
                stopOpacity={0.3}
              />
              <stop
                offset="95%"
                stopColor={lineColor}
                stopOpacity={0}
              />
            </linearGradient>
          </defs>
          <Tooltip
            content={({ active, payload }) => {
              if (active && payload && payload.length) {
                return (
                  <div className="bg-background border border-border rounded-lg p-2 shadow-lg">
                    <p className="text-xs text-muted-foreground">
                      {payload[0].payload.timestamp}
                    </p>
                    <p className="text-sm font-bold">
                      ${payload[0].value?.toLocaleString("en-US", {
                        minimumFractionDigits: 2,
                        maximumFractionDigits: 2,
                      })}
                    </p>
                  </div>
                )
              }
              return null
            }}
          />
          <Line
            type="monotone"
            dataKey="value"
            stroke={lineColor}
            strokeWidth={2}
            dot={false}
            fill="url(#sparklineGradient)"
            animationDuration={300}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
