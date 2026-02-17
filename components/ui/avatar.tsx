import { cn } from "@/lib/utils"

interface AvatarProps {
  name: string
  size?: "sm" | "md" | "lg"
  status?: "online" | "offline" | "idle"
  className?: string
}

function getInitials(name: string): string {
  return name
    .split(" ")
    .map(n => n[0])
    .join("")
    .toUpperCase()
    .slice(0, 2)
}

function getColor(name: string): string {
  const colors = [
    "from-blue-500 to-indigo-600",
    "from-purple-500 to-pink-600",
    "from-green-500 to-teal-600",
    "from-orange-500 to-red-600",
    "from-cyan-500 to-blue-600",
    "from-yellow-500 to-orange-600",
  ]
  const index = name.charCodeAt(0) % colors.length
  return colors[index]
}

export function Avatar({ name, size = "md", status, className }: AvatarProps) {
  const sizeClasses = {
    sm: "w-8 h-8 text-xs",
    md: "w-10 h-10 text-sm",
    lg: "w-14 h-14 text-lg",
  }

  const statusSizeClasses = {
    sm: "w-2 h-2 -bottom-0.5 -right-0.5",
    md: "w-2.5 h-2.5 -bottom-0.5 -right-0.5",
    lg: "w-3.5 h-3.5 bottom-0 right-0",
  }

  return (
    <div className={cn("relative flex-shrink-0", className)}>
      <div
        className={cn(
          "rounded-full flex items-center justify-center font-semibold text-white bg-gradient-to-br",
          getColor(name),
          sizeClasses[size]
        )}
      >
        {getInitials(name)}
      </div>
      {status && (
        <div
          className={cn(
            "absolute rounded-full border-2 border-slate-900",
            statusSizeClasses[size],
            status === "online" && "bg-green-400",
            status === "offline" && "bg-white/30",
            status === "idle" && "bg-yellow-400",
          )}
        />
      )}
    </div>
  )
}
