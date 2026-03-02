"use client"

import { cn } from "@/lib/utils"
import { motion, AnimatePresence } from "framer-motion"
import { Home, Users, Clock, BarChart2, ChevronLeft, ChevronRight, Layers, Terminal, CalendarClock, X, Lightbulb, Newspaper, Wallet, TrendingUp, ChevronDown, MessageSquare } from "lucide-react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { useState } from "react"

type NavItem = {
  icon: any
  label: string
  href: string
  subsections?: { label: string; href: string }[]
}

const navItems: NavItem[] = [
  { icon: Home, label: "Dashboard", href: "/" },
  { icon: Wallet, label: "Portfolio", href: "/portfolio" },
  { 
    icon: TrendingUp, 
    label: "Trading", 
    href: "/trading",
    subsections: [
      { label: "Overview", href: "/trading" },
      { label: "Themes", href: "/trading/themes" },
      { label: "Agents", href: "/trading/agents" },
      { label: "Trading Floor", href: "/trading/floor" },
      { label: "Markets", href: "/trading/markets" },
      { label: "Theses", href: "/trading/theses" },
      { label: "Positions", href: "/trading/positions" },
      { label: "Events", href: "/trading/events" },
      { label: "Memos", href: "/trading/memos" },
    ]
  },
  { icon: Lightbulb, label: "Ideas", href: "/ideas" },
  { icon: Users, label: "Agents", href: "/agents" },
  { icon: Clock, label: "Sessions", href: "/sessions" },
  { icon: BarChart2, label: "Analytics", href: "/analytics" },
  { icon: CalendarClock, label: "Crons", href: "/crons" },
  { icon: Newspaper, label: "News", href: "/news" },
  { icon: Layers, label: "Workshop", href: "/workshop" },
]

export function Sidebar() {
  const [collapsed, setCollapsed] = useState(false)
  const [mobileOpen, setMobileOpen] = useState(false)
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({
    Trading: true, // Trading expanded by default
  })
  const pathname = usePathname()

  if (pathname === "/login") return null

  const toggleSection = (label: string) => {
    setExpandedSections((prev) => ({
      ...prev,
      [label]: !prev[label],
    }))
  }

  const NavItemComponent = ({ item, isMobile = false }: { item: NavItem; isMobile?: boolean }) => {
    const isActive = pathname === item.href || (item.href !== "/" && pathname.startsWith(item.href))
    const hasSubsections = item.subsections && item.subsections.length > 0
    const isExpanded = expandedSections[item.label]

    if (hasSubsections) {
      return (
        <div key={item.label}>
          {/* Parent Item */}
          <div
            onClick={() => toggleSection(item.label)}
            className={cn(
              "flex items-center gap-3 px-2.5 py-2 rounded",
              "transition-all duration-100 cursor-pointer group",
              isActive
                ? "bg-[#0077ff15] text-[#0077ff] border-l-2 border-[#0077ff] pl-[9px]"
                : "text-[#64748b] hover:text-[#94a3b8] hover:bg-[#0d1117]"
            )}
          >
            <item.icon className={cn("w-4 h-4 flex-shrink-0", isActive && "text-[#0077ff]")} />
            <motion.span
              animate={{ opacity: collapsed ? 0 : 1, width: collapsed ? 0 : "auto" }}
              transition={{ duration: 0.15 }}
              className="text-xs font-medium whitespace-nowrap overflow-hidden tracking-wide uppercase flex-1"
            >
              {item.label}
            </motion.span>
            {!collapsed && (
              <motion.div
                animate={{ rotate: isExpanded ? 180 : 0 }}
                transition={{ duration: 0.2 }}
              >
                <ChevronDown className="w-3.5 h-3.5" />
              </motion.div>
            )}
          </div>

          {/* Subsections */}
          <AnimatePresence>
            {isExpanded && !collapsed && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: "auto", opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                transition={{ duration: 0.2 }}
                className="overflow-hidden"
              >
                <div className="ml-6 space-y-0.5 mt-0.5">
                  {item.subsections?.map((sub) => {
                    const isSubActive = pathname === sub.href
                    return (
                      <Link key={sub.href} href={sub.href}>
                        <div
                          className={cn(
                            "flex items-center gap-2 px-2.5 py-1.5 rounded text-xs",
                            "transition-all duration-100 cursor-pointer",
                            isSubActive
                              ? "bg-[#0077ff10] text-[#0077ff] font-medium"
                              : "text-[#64748b] hover:text-[#94a3b8] hover:bg-[#0d1117]"
                          )}
                        >
                          <span className="w-1 h-1 rounded-full bg-current" />
                          <span className="tracking-wide">{sub.label}</span>
                        </div>
                      </Link>
                    )
                  })}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      )
    }

    // Regular nav item (no subsections)
    return (
      <Link key={item.href} href={item.href}>
        <div
          className={cn(
            "flex items-center gap-3 px-2.5 py-2 rounded",
            "transition-all duration-100 cursor-pointer group",
            isActive
              ? "bg-[#0077ff15] text-[#0077ff] border-l-2 border-[#0077ff] pl-[9px]"
              : "text-[#64748b] hover:text-[#94a3b8] hover:bg-[#0d1117]"
          )}
        >
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
  }

  return (
    <>
      {/* ── Desktop Sidebar ─────────────────────────────── */}
      <motion.aside
        animate={{ width: collapsed ? 56 : 220 }}
        transition={{ duration: 0.2 }}
        className={cn(
          "hidden md:flex",
          "fixed left-0 top-0 h-screen z-20",
          "bg-[#0d1117] border-r border-[#1e2d3d]",
          "flex-col py-5 px-2"
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
        <nav className="flex-1 space-y-0.5 overflow-y-auto">
          {navItems.map((item) => (
            <NavItemComponent key={item.label} item={item} />
          ))}
        </nav>

        {/* Version */}
        <motion.div
          animate={{ opacity: collapsed ? 0 : 1 }}
          className="px-2.5 pt-4 border-t border-[#1e2d3d]"
        >
          <p className="text-[#1e3a5f] text-xs font-mono">v0.1.0</p>
        </motion.div>
      </motion.aside>

      {/* ── Mobile Bottom Nav ───────────────────────────── */}
      <nav className="md:hidden fixed bottom-0 left-0 right-0 z-30 bg-[#0d1117] border-t border-[#1e2d3d] h-16 flex items-center justify-around px-2">
        {navItems.slice(0, 5).map((item) => {
          const isActive = pathname === item.href || (item.href !== "/" && pathname.startsWith(item.href))
          return (
            <Link key={item.href} href={item.href} className="flex-1">
              <div
                className={cn(
                  "flex flex-col items-center justify-center gap-0.5 py-1 rounded transition-colors",
                  isActive ? "text-[#0077ff]" : "text-[#64748b]"
                )}
              >
                <item.icon className="w-5 h-5" />
                <span className="text-[9px] font-mono uppercase tracking-wide">{item.label}</span>
              </div>
            </Link>
          )
        })}
      </nav>

      {/* ── Mobile Drawer Overlay (optional, triggered by hamburger) ── */}
      <AnimatePresence>
        {mobileOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="md:hidden fixed inset-0 bg-black/60 z-40"
              onClick={() => setMobileOpen(false)}
            />
            <motion.aside
              initial={{ x: "-100%" }}
              animate={{ x: 0 }}
              exit={{ x: "-100%" }}
              transition={{ type: "tween", duration: 0.2 }}
              className="md:hidden fixed left-0 top-0 h-screen w-64 z-50 bg-[#0d1117] border-r border-[#1e2d3d] flex flex-col py-5 px-2"
            >
              <div className="flex items-center justify-between mb-6 px-2">
                <div className="flex items-center gap-2">
                  <Terminal className="w-4 h-4 text-[#0077ff]" />
                  <span className="text-sm font-semibold text-white tracking-wide">MISSION CTRL</span>
                </div>
                <button onClick={() => setMobileOpen(false)} className="p-1 rounded hover:bg-[#1e2d3d]">
                  <X className="w-4 h-4 text-[#64748b]" />
                </button>
              </div>
              <nav className="flex-1 space-y-0.5 overflow-y-auto">
                {navItems.map((item) => (
                  <NavItemComponent key={item.label} item={item} isMobile />
                ))}
              </nav>
            </motion.aside>
          </>
        )}
      </AnimatePresence>
    </>
  )
}
