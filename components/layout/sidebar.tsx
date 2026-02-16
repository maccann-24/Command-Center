"use client"

import { cn } from "@/lib/utils"
import { motion } from "framer-motion"
import { Home, Users, Activity, Settings, ChevronLeft, ChevronRight } from "lucide-react"
import Link from "next/link"
import { useState } from "react"

const navItems = [
  { icon: Home, label: "Dashboard", href: "/" },
  { icon: Users, label: "Agents", href: "/agents" },
  { icon: Activity, label: "Sessions", href: "/sessions" },
  { icon: Settings, label: "Settings", href: "/settings" },
]

export function Sidebar() {
  const [collapsed, setCollapsed] = useState(false)

  return (
    <motion.aside
      animate={{ width: collapsed ? 80 : 240 }}
      className={cn(
        "fixed left-0 top-0 h-screen",
        "bg-white/5 backdrop-blur-xl border-r border-white/10",
        "flex flex-col p-4 transition-all duration-300"
      )}
    >
      {/* Logo / Branding */}
      <div className="flex items-center justify-between mb-8">
        <motion.h1 
          animate={{ opacity: collapsed ? 0 : 1 }}
          className="text-xl font-bold text-white"
        >
          Mission Control
        </motion.h1>
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="p-2 rounded-lg hover:bg-white/10 transition-colors"
        >
          {collapsed ? (
            <ChevronRight className="w-5 h-5 text-white" />
          ) : (
            <ChevronLeft className="w-5 h-5 text-white" />
          )}
        </button>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 space-y-2">
        {navItems.map((item) => (
          <Link key={item.href} href={item.href}>
            <div className={cn(
              "flex items-center gap-3 px-3 py-2.5 rounded-lg",
              "text-white/70 hover:text-white hover:bg-white/10",
              "transition-all duration-200 cursor-pointer"
            )}>
              <item.icon className="w-5 h-5 flex-shrink-0" />
              <motion.span
                animate={{ opacity: collapsed ? 0 : 1, width: collapsed ? 0 : "auto" }}
                className="font-medium whitespace-nowrap overflow-hidden"
              >
                {item.label}
              </motion.span>
            </div>
          </Link>
        ))}
      </nav>
    </motion.aside>
  )
}
