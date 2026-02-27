"use client"

import { usePathname } from "next/navigation"
import { useState, useEffect } from "react"
import { supabase } from "@/lib/supabase"
import { Button } from "@/components/ui/button"

function getPageTitle(pathname: string): string {
  if (pathname === "/") return "Dashboard"
  if (pathname === "/portfolio") return "Portfolio"
  if (pathname.startsWith("/agents") && pathname.includes("/settings")) return "Agent Settings"
  if (pathname.startsWith("/agents") && pathname !== "/agents") return "Agent Details"
  if (pathname === "/agents") return "Agents"
  if (pathname.startsWith("/sessions") && pathname !== "/sessions") return "Session Details"
  if (pathname === "/sessions") return "Sessions"
  if (pathname === "/analytics") return "Analytics"
  if (pathname === "/workshop") return "Workshop"
  if (pathname === "/crons") return "Cron Jobs"
  if (pathname === "/ideas") return "Ideas"
  if (pathname === "/portfolio") return "Portfolio"
  return "Mission Control"
}

export function Header() {
  const pathname = usePathname()
  if (pathname === "/login") return null

  const title = getPageTitle(pathname)
  const [time, setTime] = useState("")
  const [userEmail, setUserEmail] = useState<string | null>(null)

  useEffect(() => {
    const update = () =>
      setTime(
        new Date().toLocaleTimeString("en-US", {
          hour12: false,
          hour: "2-digit",
          minute: "2-digit",
          second: "2-digit",
        })
      )
    update()
    const interval = setInterval(update, 1000)
    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    let mounted = true

    async function load() {
      const { data } = await supabase.auth.getSession()
      if (!mounted) return
      setUserEmail(data.session?.user.email ?? null)
    }

    load()

    const { data: sub } = supabase.auth.onAuthStateChange((_event, session) => {
      setUserEmail(session?.user.email ?? null)
    })

    return () => {
      mounted = false
      sub.subscription.unsubscribe()
    }
  }, [])

  async function logout() {
    await supabase.auth.signOut()
  }

  return (
    <header className="fixed top-0 right-0 left-0 md:left-[220px] h-14 z-10 bg-[#0d1117] border-b border-[#1e2d3d] flex items-center px-4 md:px-6">
      <div className="flex items-center gap-3">
        <span className="text-[#0077ff] text-xs font-mono font-medium tracking-widest uppercase">
          {title}
        </span>
      </div>
      <div className="ml-auto flex items-center gap-3 md:gap-4">
        {/* Live indicator */}
        <div className="flex items-center gap-1.5 md:gap-2">
          <span className="relative flex h-1.5 w-1.5">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#00d084] opacity-75" />
            <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-[#00d084]" />
          </span>
          <span className="text-[#00d084] text-xs font-mono">LIVE</span>
        </div>
        <span className="hidden sm:block text-[#1e3a5f] text-xs font-mono">{time}</span>
        {userEmail && (
          <span className="hidden md:block text-white/40 text-xs font-mono max-w-[240px] truncate">
            {userEmail}
          </span>
        )}
        <Button variant="ghost" size="sm" onClick={logout}>
          Logout
        </Button>
        <div className="w-7 h-7 rounded-sm bg-[#0077ff15] border border-[#0077ff30] flex items-center justify-center">
          <span className="text-[#0077ff] text-xs font-bold font-mono">MC</span>
        </div>
      </div>
    </header>
  )
}
