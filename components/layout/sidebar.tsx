"use client"

import { cn } from "@/lib/utils"
import { motion } from "framer-motion"
import { Home, Users, Clock, BarChart2, ChevronLeft, ChevronRight, Layers, Terminal, CalendarClock } from "lucide-react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { useState } from "react"

const navItems = [
  { icon: Home, label: "Dashboard", href: "/" },
  { icon: Users, label: "Agents", href: "/agents" },
  { icon: Clock, label: "Sessions", href: "/sessions" },
  { icon: BarChart2, label: "Analytics", href: "/analytics" },
  { icon: CalendarClock, label: "Crons", href: "/crons" },
  { icon: Layers, label: "Workshop", href: "/workshop" },
]

export function Sidebar() {
  const [collapsed, setCollapsed] = useState(false)
  const pathname = usePathname()

  return (
    <motion.aside
      animate={{ width: collapsed ? 56 : 220 }}
      transition={{ duration: 0.2 }}
      className={cn(
        "fixed left-0 top-0 h-screen z-20",
        "bg-[#0d1117] border-r border-[#1e2d3d]",
        "flex flex-col py-5 px-2"
      )}
    >
      {/* Logo */}
      <div className="flex items-center justify-between mb-6 px-2">
        <motion.div
          animate={{ opacity: collapsed ? 0 : 1 }}
          className="flex items-center gap-2 overflow-hidden"
        >
          <Terminal className="w-4 h-4 text-[#0077ff] flex-shrink-0" />
          <span className="text-sm font-semibold text-white whitespace-nowrap tracking-wide">
            MISSION CTRL
          </span>
        </motion.div>
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="p-1 rounded hover:bg-[#1e2d3d] transition-colors flex-shrink-0"
        >
          {collapsed ? (
            <ChevronRight className="w-3.5 h-3.5 text-[#64748b]" />
          ) : (
            <ChevronLeft className="w-3.5 h-3.5 text-[#64748b]" />
          )}
        </button>
      </div>

      {/* Nav */}
      <nav className="flex-1 space-y-0.5">
        {navItems.map((item) => {
          const isActive = pathname === item.href ||
            (item.href !== "/" && pathname.startsWith(item.href))

          return (
            <Link key={item.href} href={item.href}>
              <div className={cn(
                "flex items-center gap-3 px-2.5 py-2 rounded",
                "transition-all duration-100 cursor-pointer group",
                isActive
                  ? "bg-[#0077ff15] text-[#0077ff] border-l-2 border-[#0077ff] pl-[9px]"
                  : "text-[#64748b] hover:text-[#94a3b8] hover:bg-[#0d1117]"
              )}>
                <item.icon className={cn("w-4 h-4 flex-shrink-0", isActive && "text-[#0077ff]")} />
                <motion.span
                  animate={{ opacity: collapsed ? 0 : 1, width: collapsed ? 0 : "auto" }}
                  transition={{ duration: 0.15 }}
                  className="text-xs font-medium whitespace-nowrap overflow-hidden tracking-wide uppercase"
                >
                  {item.label}
                </motion.span>
              </div>
            </Link>
          )
        })}
      </nav>

      {/* Version */}
      <motion.div
        animate={{ opacity: collapsed ? 0 : 1 }}
        className="px-2.5 pt-4 border-t border-[#1e2d3d]"
      >
        <p className="text-[#1e3a5f] text-xs font-mono">v0.1.0</p>
      </motion.div>
    </motion.aside>
  )
}
