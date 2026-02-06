import { TestAnimation } from "@/components/test-animation"

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24 bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <div className="z-10 w-full max-w-2xl space-y-8">
        <div className="text-center space-y-4">
          <h1 className="text-5xl font-bold text-white">
            Mission Control
          </h1>
          <p className="text-lg text-white/70">
            AI Agent Management Dashboard
          </p>
        </div>
        
        <TestAnimation />
        
        <div className="text-center text-sm text-white/50">
          Phase 1.1.3 Complete ✅
        </div>
      </div>
    </main>
  )
}
