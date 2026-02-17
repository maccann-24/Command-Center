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
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
      onClick={onClick}
      className={cn(
        "rounded-sm border border-[#1e2d3d]",
        "bg-[#0d1117]",
        variant === "hover" && "cursor-pointer transition-all duration-150 hover:border-[#0077ff40] hover:bg-[#0d1520]",
        variant === "active" && "border-[#0077ff40] bg-[#0d1520]",
        className
      )}
    >
      {children}
    </motion.div>
  )
}
