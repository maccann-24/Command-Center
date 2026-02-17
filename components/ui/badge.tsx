import { cn } from "@/lib/utils"
import { ReactNode } from "react"

interface BadgeProps {
  children: ReactNode
  variant?: "success" | "warning" | "error" | "info" | "default"
  pulse?: boolean
  className?: string
}

export function Badge({ children, variant = "default", pulse = false, className }: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium",
        variant === "success" && "bg-green-500/20 text-green-300 border border-green-500/30",
        variant === "warning" && "bg-yellow-500/20 text-yellow-300 border border-yellow-500/30",
        variant === "error" && "bg-red-500/20 text-red-300 border border-red-500/30",
        variant === "info" && "bg-blue-500/20 text-blue-300 border border-blue-500/30",
        variant === "default" && "bg-white/10 text-white/70 border border-white/20",
        className
      )}
    >
      {pulse && (
        <span className="relative flex h-2 w-2">
          <span className={cn(
            "animate-ping absolute inline-flex h-full w-full rounded-full opacity-75",
            variant === "success" && "bg-green-400",
            variant === "warning" && "bg-yellow-400",
            variant === "error" && "bg-red-400",
            variant === "info" && "bg-blue-400",
          )} />
          <span className={cn(
            "relative inline-flex rounded-full h-2 w-2",
            variant === "success" && "bg-green-400",
            variant === "warning" && "bg-yellow-400",
            variant === "error" && "bg-red-400",
            variant === "info" && "bg-blue-400",
          )} />
        </span>
      )}
      {children}
    </span>
  )
}
