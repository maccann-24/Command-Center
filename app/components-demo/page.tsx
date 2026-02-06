"use client"

import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Avatar } from "@/components/ui/avatar"
import { Sparkles, Zap } from "lucide-react"

export default function ComponentsDemo() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-8">
      <div className="max-w-6xl mx-auto space-y-8">
        <div className="text-center space-y-2">
          <h1 className="text-4xl font-bold text-white">Component Showcase</h1>
          <p className="text-white/70">Glass morphism UI components</p>
        </div>

        <section className="space-y-4">
          <h2 className="text-2xl font-semibold text-white">Cards</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card variant="default" className="p-6">
              <h3 className="text-white font-semibold mb-2">Default Card</h3>
              <p className="text-white/70 text-sm">Standard glass effect</p>
            </Card>
            <Card variant="hover" className="p-6">
              <h3 className="text-white font-semibold mb-2">Hover Card</h3>
              <p className="text-white/70 text-sm">Scales on hover</p>
            </Card>
            <Card variant="active" className="p-6">
              <h3 className="text-white font-semibold mb-2">Active Card</h3>
              <p className="text-white/70 text-sm">Enhanced shadow</p>
            </Card>
          </div>
        </section>

        <section className="space-y-4">
          <h2 className="text-2xl font-semibold text-white">Buttons</h2>
          <Card className="p-6">
            <div className="flex flex-wrap gap-4">
              <Button variant="primary">Primary</Button>
              <Button variant="secondary">Secondary</Button>
              <Button variant="ghost">Ghost</Button>
              <Button variant="primary" size="sm">Small</Button>
              <Button variant="primary" size="lg">Large</Button>
            </div>
          </Card>
        </section>

        <section className="space-y-4">
          <h2 className="text-2xl font-semibold text-white">Badges</h2>
          <Card className="p-6">
            <div className="flex flex-wrap gap-3">
              <Badge variant="success" pulse>Active</Badge>
              <Badge variant="warning">Idle</Badge>
              <Badge variant="error">Error</Badge>
              <Badge variant="info">Info</Badge>
            </div>
          </Card>
        </section>

        <section className="space-y-4">
          <h2 className="text-2xl font-semibold text-white">Avatars</h2>
          <Card className="p-6">
            <div className="flex flex-wrap items-center gap-6">
              <Avatar name="Agent Alpha" size="sm" status="online" />
              <Avatar name="Agent Beta" size="md" status="online" />
              <Avatar name="Agent Gamma" size="lg" status="offline" />
            </div>
          </Card>
        </section>

        <section className="space-y-4">
          <h2 className="text-2xl font-semibold text-white">Combined Example</h2>
          <Card variant="hover" className="p-6">
            <div className="flex items-start gap-4">
              <Avatar name="Agent Alpha" size="lg" status="online" />
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <h3 className="text-white font-semibold">Agent Alpha</h3>
                  <Badge variant="success" pulse>Active</Badge>
                </div>
                <p className="text-white/70 text-sm mb-4">
                  Running GPT-4 | 127 sessions | $42.50 spent
                </p>
                <div className="flex gap-2">
                  <Button variant="primary" size="sm">
                    <Sparkles className="w-4 h-4 mr-1" />
                    View Details
                  </Button>
                  <Button variant="ghost" size="sm">
                    <Zap className="w-4 h-4 mr-1" />
                    Restart
                  </Button>
                </div>
              </div>
            </div>
          </Card>
        </section>

      </div>
    </div>
  )
}
