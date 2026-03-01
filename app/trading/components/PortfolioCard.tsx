import { Card } from "@/components/ui/card"

type PortfolioCardProps = {
  title: string
  value: number
  format: "currency" | "percentage" | "pnl"
  icon?: string
}

export default function PortfolioCard({
  title,
  value,
  format,
  icon,
}: PortfolioCardProps) {
  // Format value based on type
  let displayValue = ""
  let valueClass = "text-3xl font-bold"

  if (format === "currency") {
    displayValue = `$${value.toLocaleString("en-US", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    })}`
  } else if (format === "percentage") {
    displayValue = `${value.toFixed(1)}%`
  } else if (format === "pnl") {
    displayValue = `$${value.toLocaleString("en-US", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    })}`
    // Color code P&L
    if (value > 0) {
      valueClass += " text-green-500"
    } else if (value < 0) {
      valueClass += " text-red-500"
    } else {
      valueClass += " text-muted-foreground"
    }
  }

  return (
    <Card className="p-6">
      <div className="flex items-start justify-between">
        <div className="space-y-1">
          <p className="text-sm font-medium text-muted-foreground">{title}</p>
          <p className={valueClass}>{displayValue}</p>
        </div>
        {icon && <span className="text-2xl">{icon}</span>}
      </div>
    </Card>
  )
}
