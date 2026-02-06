import { cn } from "@/lib/utils"
import { motion, HTMLMotionProps } from "framer-motion"
import { ReactNode } from "react"

interface CardProps extends Omit<HTMLMotionProps<"div">, "children"> {
  children: ReactNode
  variant?: "default" | "hover" | "active"
  animate?: boolean
}

export function Card({ 
  children, 
  variant = "default", 
  animate = true,
  className,
  ...props 
}: CardProps) {
  const baseStyles = cn(
    "rounded-2xl backdrop-blur-lg border",
    "shadow-xl transition-all duration-300",
    variant === "default" && "bg-white/10 border-white/20",
    variant === "hover" && "bg-white/15 border-white/30 hover:scale-[1.02]",
    variant === "active" && "bg-white/20 border-white/40 shadow-2xl",
    className
  )

  if (!animate) {
    return <div className={baseStyles}>{children}</div>
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className={baseStyles}
      {...props}
    >
      {children}
    </motion.div>
  )
}
