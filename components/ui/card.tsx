"use client"

import { cn } from "@/lib/utils"
import { motion } from "framer-motion"
import { ReactNode } from "react"

interface CardProps {
  children: ReactNode
  className?: string
  variant?: "default" | "hover" | "active"
  onClick?: () => void
}

export function Card({ children, className, variant = "default", onClick }: CardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      onClick={onClick}
      className={cn(
        "rounded-2xl border border-white/10",
        "bg-white/5 backdrop-blur-xl",
        "shadow-xl shadow-black/10",
        variant === "hover" && "cursor-pointer transition-all duration-200 hover:bg-white/10 hover:border-white/20 hover:shadow-2xl hover:-translate-y-0.5",
        variant === "active" && "bg-white/15 border-white/20",
        className
      )}
    >
      {children}
    </motion.div>
  )
}
