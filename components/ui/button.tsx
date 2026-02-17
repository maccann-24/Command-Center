"use client"

import { cn } from "@/lib/utils"
import { ReactNode } from "react"

interface ButtonProps {
  children: ReactNode
  variant?: "primary" | "secondary" | "ghost"
  size?: "sm" | "md" | "lg"
  isLoading?: boolean
  onClick?: () => void
  className?: string
  disabled?: boolean
  type?: "button" | "submit" | "reset"
}

export function Button({
  children,
  variant = "primary",
  size = "md",
  isLoading = false,
  onClick,
  className,
  disabled,
  type = "button",
}: ButtonProps) {
  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled || isLoading}
      className={cn(
        "inline-flex items-center justify-center rounded-xl font-medium transition-all duration-150",
        "disabled:opacity-50 disabled:cursor-not-allowed",
        // Variants
        variant === "primary" && "bg-brand-primary hover:bg-brand-primary/90 text-white shadow-lg shadow-brand-primary/20",
        variant === "secondary" && "bg-white/10 hover:bg-white/15 text-white border border-white/20",
        variant === "ghost" && "bg-transparent hover:bg-white/10 text-white/70 hover:text-white",
        // Sizes
        size === "sm" && "px-3 py-1.5 text-sm gap-1.5",
        size === "md" && "px-4 py-2 text-sm gap-2",
        size === "lg" && "px-6 py-3 text-base gap-2",
        className
      )}
    >
      {isLoading ? (
        <>
          <svg
            className="animate-spin -ml-1 mr-2 h-4 w-4"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
          </svg>
          Loading...
        </>
      ) : (
        children
      )}
    </button>
  )
}
