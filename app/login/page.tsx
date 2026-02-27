"use client";

import { useState } from "react";
import { supabase } from "@/lib/supabase";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Terminal } from "lucide-react";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const { error: signInError } = await supabase.auth.signInWithPassword({
        email,
        password,
      });
      if (signInError) throw signInError;
      // AuthGate will redirect after session exists.
    } catch (err: any) {
      setError(err?.message ?? "Login failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-[70vh] flex items-center justify-center">
      <Card className="w-full max-w-md p-6">
        <div className="flex items-center gap-2 mb-4">
          <div className="p-2 rounded-sm bg-[#0077ff15] border border-[#0077ff30]">
            <Terminal className="w-4 h-4 text-[#0077ff]" />
          </div>
          <div>
            <h1 className="text-lg font-semibold text-white">Mission Control</h1>
            <p className="text-xs text-white/50">Sign in to continue</p>
          </div>
        </div>

        <form onSubmit={onSubmit} className="space-y-3">
          <div className="space-y-1">
            <label className="text-xs font-mono text-white/70">Email</label>
            <input
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              type="email"
              required
              className="w-full bg-black/20 border border-white/10 rounded-sm px-3 py-2 text-sm text-white outline-none focus:border-[#0077ff60]"
              placeholder="you@example.com"
            />
          </div>

          <div className="space-y-1">
            <label className="text-xs font-mono text-white/70">Password</label>
            <input
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              type="password"
              required
              className="w-full bg-black/20 border border-white/10 rounded-sm px-3 py-2 text-sm text-white outline-none focus:border-[#0077ff60]"
              placeholder="••••••••"
            />
          </div>

          {error && (
            <div className="text-xs text-red-300 bg-red-500/10 border border-red-500/20 rounded-sm px-3 py-2">
              {error}
            </div>
          )}

          <Button type="submit" disabled={loading} className="w-full">
            {loading ? "Signing in…" : "Sign in"}
          </Button>

          <p className="text-[11px] text-white/40">
            You must have a Supabase Auth user created for this project.
          </p>
        </form>
      </Card>
    </div>
  );
}
