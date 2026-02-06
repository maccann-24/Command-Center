import { cn } from "@/lib/utils"

interface AvatarProps {
  name: string
  src?: string
  size?: "sm" | "md" | "lg"
  status?: "online" | "offline"
  className?: string
}

export function Avatar({ name, src, size = "md", status, className }: AvatarProps) {
  const initials = name
    .split(" ")
    .map(n => n[0])
    .join("")
    .toUpperCase()
    .slice(0, 2)
return (
    <div className={cn("relative inline-block", className)}>
      <div
        className={cn(
          "rounded-full flex items-center justify-center font-semibold bg-gradient-to-br from-brand-primary to-brand-secondary text-white",
          size === "sm" && "w-8 h-8 text-xs",
          size === "md" && "w-12 h-12 text-sm",
          size === "lg" && "w-16 h-16 text-base"
        )}
      >
        {src ? (
          <img src={src} alt={name} className="w-full h-full rounded-full object-cover" />
        ) : (
          initials
        )}
      </div>
      
      {status && (
        <span
          className={cn(
            "absolute bottom-0 right-0 rounded-full border-2 border-slate-900",
            size === "sm" && "w-2.5 h-2.5",
            size === "md" && "w-3 h-3",
            size === "lg" && "w-4 h-4",
            status === "online" && "bg-status-success",
            status === "offline" && "bg-gray-400"
          )}
        />
      )}
    </div>
  )
}
