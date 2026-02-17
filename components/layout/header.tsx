"use client"

import { usePathname } from "next/navigation"

function getPageTitle(pathname: string): string {
  if (pathname === "/") return "Dashboard"
  if (pathname.startsWith("/agents") && pathname.includes("/settings")) return "Agent Settings"
  if (pathname.startsWith("/agents") && pathname !== "/agents") return "Agent Details"
  if (pathname === "/agents") return "Agents"
  if (pathname.startsWith("/sessions") && pathname !== "/sessions") return "Session Details"
  if (pathname === "/sessions") return "Sessions"
  if (pathname === "/analytics") return "Analytics"
  return "Mission Control"
}

export function Header() {
  const pathname = usePathname()
  const title = getPageTitle(pathname)

  return (
    <header className="fixed top-0 right-0 left-60 h-16 z-10 bg-white/5 backdrop-blur-xl border-b border-white/10 flex items-center px-8">
      <div className="flex items-center gap-3">
        <h2 className="text-white/80 font-semibold">{title}</h2>
      </div>
      <div className="ml-auto flex items-center gap-3">
        <div className="w-8 h-8 rounded-full bg-brand-primary/30 border border-brand-primary/50 flex items-center justify-center">
          <span className="text-white text-xs font-bold">MC</span>
        </div>
      </div>
    </header>
  )
}
