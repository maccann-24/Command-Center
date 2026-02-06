import { cn } from "@/lib/utils"
import { ReactNode } from "react"

interface BadgeProps {
  children: ReactNode
  variant?: "success" | "warning" | "error" | "info"
  pulse?: boolean
  className?: string
}

export function Badge({ children, variant = "info", pulse = false, className }: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium",
        variant === "success" && "bg-status-success/20 text-green-300",
        variant === "warning" && "bg-status-warning/20 text-yellow-300",
        variant === "error" && "bg-status-error/20 text-red-300",
        variant === "info" && "bg-status-info/20 text-blue-300",
        className
      )}
    >
      {pulse && (
        <span className={cn(
          "w-2 h-2 rounded-full animate-pulse",
          variant === "success" && "bg-status-success",
          variant === "warning" && "bg-status-warning",
          variant === "error" && "bg-status-error",
          variant === "info" && "bg-status-info"
        )} />
      )}
      {children}
    </span>
  )
}
