"use client"

import { Card } from "@/components/ui/card"
import { Avatar } from "@/components/ui/avatar"
import { Search } from "lucide-react"

export function Header() {
  return (
    <header className="fixed top-0 right-0 left-60 h-16 z-10">
      <Card animate={false} className="h-full mx-4 mt-4 px-6 flex items-center justify-between">
        {/* Search Bar */}
        <div className="flex items-center gap-3 flex-1 max-w-md">
          <Search className="w-5 h-5 text-white/50" />
          <input
            type="text"
            placeholder="Search agents, sessions..."
            className="bg-transparent text-white placeholder:text-white/40 outline-none w-full"
          />
        </div>

        {/* User Profile */}
        <div className="flex items-center gap-3">
          <div className="text-right">
            <div className="text-sm font-medium text-white">Matthew Cannon</div>
            <div className="text-xs text-white/50">Admin</div>
          </div>
          <Avatar name="Matthew Cannon" size="md" status="online" />
        </div>
      </Card>
    </header>
  )
}
