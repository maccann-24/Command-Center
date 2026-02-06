"use client"

import { motion } from "framer-motion"
import { Sparkles } from "lucide-react"
import { cn } from "@/lib/utils"

export function TestAnimation() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className={cn(
        "p-6 rounded-2xl",
        "bg-white/10 backdrop-blur-lg",
        "border border-white/20",
        "shadow-xl shadow-black/5",
        "hover:bg-white/15 hover:scale-105",
        "transition-all duration-300"
      )}
    >
      <div className="flex items-center gap-4">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
        >
          <Sparkles className="w-8 h-8 text-blue-400" />
        </motion.div>
        <div>
          <h3 className="text-lg font-semibold text-white">
            Animation Test
          </h3>
          <p className="text-sm text-white/70">
            Framer Motion + Lucide + Tailwind working! ✨
          </p>
        </div>
      </div>
    </motion.div>
  )
}
