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
        "inline-flex items-center gap-1.5 px-1.5 py-0.5 rounded-sm text-xs font-mono font-medium tracking-wide",
        variant === "success" && "bg-[#00d08415] text-[#00d084] border border-[#00d08430]",
        variant === "warning" && "bg-[#f5a62315] text-[#f5a623] border border-[#f5a62330]",
        variant === "error" && "bg-[#ff3b4715] text-[#ff3b47] border border-[#ff3b4730]",
        variant === "info" && "bg-[#0077ff15] text-[#0077ff] border border-[#0077ff30]",
        variant === "default" && "bg-[#1e2d3d] text-[#64748b] border border-[#1e2d3d]",
        className
      )}
    >
      {pulse && (
        <span className="relative flex h-1.5 w-1.5">
          <span className={cn(
            "animate-ping absolute inline-flex h-full w-full rounded-full opacity-75",
            variant === "success" && "bg-[#00d084]",
            variant === "warning" && "bg-[#f5a623]",
            variant === "error" && "bg-[#ff3b47]",
            variant === "info" && "bg-[#0077ff]",
          )} />
          <span className={cn(
            "relative inline-flex rounded-full h-1.5 w-1.5",
            variant === "success" && "bg-[#00d084]",
            variant === "warning" && "bg-[#f5a623]",
            variant === "error" && "bg-[#ff3b47]",
            variant === "info" && "bg-[#0077ff]",
          )} />
        </span>
      )}
      {children}
    </span>
  )
}
