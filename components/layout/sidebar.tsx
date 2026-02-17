"use client"

import { cn } from "@/lib/utils"
import { motion } from "framer-motion"
import { Home, Users, Clock, BarChart2, ChevronLeft, ChevronRight, Layers } from "lucide-react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { useState } from "react"

const navItems = [
  { icon: Home, label: "Dashboard", href: "/" },
  { icon: Users, label: "Agents", href: "/agents" },
  { icon: Clock, label: "Sessions", href: "/sessions" },
  { icon: BarChart2, label: "Analytics", href: "/analytics" },
  { icon: Layers, label: "Workshop", href: "/workshop" },
]

export function Sidebar() {
  const [collapsed, setCollapsed] = useState(false)
  const pathname = usePathname()

  return (
    <motion.aside
      animate={{ width: collapsed ? 72 : 240 }}
      transition={{ duration: 0.2 }}
      className={cn(
        "fixed left-0 top-0 h-screen z-20",
        "bg-white/5 backdrop-blur-xl border-r border-white/10",
        "flex flex-col py-6 px-3"
      )}
    >
      <div className="flex items-center justify-between mb-8 px-2">
        <motion.span
          animate={{ opacity: collapsed ? 0 : 1 }}
          className="text-lg font-bold text-white whitespace-nowrap overflow-hidden"
        >
          Mission Control
        </motion.span>
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="p-1.5 rounded-lg hover:bg-white/10 transition-colors flex-shrink-0"
        >
          {collapsed ? (
            <ChevronRight className="w-4 h-4 text-white/70" />
          ) : (
            <ChevronLeft className="w-4 h-4 text-white/70" />
          )}
        </button>
      </div>

      <nav className="flex-1 space-y-1">
        {navItems.map((item) => {
          const isActive = pathname === item.href ||
            (item.href !== "/" && pathname.startsWith(item.href))

          return (
            <Link key={item.href} href={item.href}>
              <div className={cn(
                "flex items-center gap-3 px-3 py-2.5 rounded-xl",
                "transition-all duration-150 cursor-pointer",
                isActive
                  ? "bg-brand-primary/25 text-white border border-brand-primary/40"
                  : "text-white/60 hover:text-white hover:bg-white/10"
              )}>
                <item.icon className="w-5 h-5 flex-shrink-0" />
                <motion.span
                  animate={{ opacity: collapsed ? 0 : 1, width: collapsed ? 0 : "auto" }}
                  transition={{ duration: 0.15 }}
                  className="font-medium whitespace-nowrap overflow-hidden text-sm"
                >
                  {item.label}
                </motion.span>
              </div>
            </Link>
          )
        })}
      </nav>

      <motion.div
        animate={{ opacity: collapsed ? 0 : 1 }}
        className="px-3 pt-4 border-t border-white/10"
      >
        <p className="text-white/30 text-xs">Mission Control v0.1</p>
      </motion.div>
    </motion.aside>
  )
}
