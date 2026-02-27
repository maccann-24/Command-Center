"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { supabase } from "@/lib/supabase";
import { Card } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Activity, Shield, TrendingUp, Wallet } from "lucide-react";

type PortfolioRow = {
  id: number;
  cash: number;
  total_value: number;
  deployed_pct: number;
  daily_pnl: number;
  all_time_pnl: number;
  updated_at: string | null;
};

function formatUsd(n: number) {
  return n.toLocaleString("en-US", { style: "currency", currency: "USD" });
}

function formatPct(n: number) {
  return `${n.toFixed(1)}%`;
}

function clamp01(n: number) {
  if (Number.isNaN(n)) return 0;
  return Math.max(0, Math.min(1, n));
}

function relativeTime(iso: string | null) {
  if (!iso) return "—";
  const d = new Date(iso);
  const diff = Math.max(0, Date.now() - d.getTime());
  const s = Math.floor(diff / 1000);
  if (s < 10) return "just now";
  if (s < 60) return `${s}s ago`;
  const m = Math.floor(s / 60);
  if (m < 60) return `${m}m ago`;
  const h = Math.floor(m / 60);
  return `${h}h ago`;
}

export default function PortfolioPage() {
  const [loading, setLoading] = useState(true);
  const [portfolio, setPortfolio] = useState<PortfolioRow | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [liveFlash, setLiveFlash] = useState(false);
  const liveFlashTimeout = useRef<ReturnType<typeof setTimeout> | null>(null);

  const flashLive = useCallback(() => {
    setLiveFlash(true);
    if (liveFlashTimeout.current) clearTimeout(liveFlashTimeout.current);
    liveFlashTimeout.current = setTimeout(() => setLiveFlash(false), 1500);
  }, []);

  const fetchPortfolio = useCallback(async () => {
    setError(null);
    const { data, error: qErr } = await supabase
      .from("portfolio")
      .select("*")
      .eq("id", 1)
      .single();

    if (qErr) {
      setPortfolio(null);
      setError(qErr.message);
    } else {
      setPortfolio(data as PortfolioRow);
    }

    setLoading(false);
  }, []);

  useEffect(() => {
    fetchPortfolio();
  }, [fetchPortfolio]);

  useEffect(() => {
    const channel = supabase
      .channel("portfolio-realtime")
      .on(
        "postgres_changes",
        { event: "*", schema: "public", table: "portfolio", filter: "id=eq.1" },
        () => {
          flashLive();
          fetchPortfolio();
        }
      )
      .subscribe();

    return () => {
      if (liveFlashTimeout.current) clearTimeout(liveFlashTimeout.current);
      supabase.removeChannel(channel);
    };
  }, [fetchPortfolio, flashLive]);

  const derived = useMemo(() => {
    if (!portfolio) return null;

    const daily = portfolio.daily_pnl ?? 0;
    const allTime = portfolio.all_time_pnl ?? 0;
    const deployed = portfolio.deployed_pct ?? 0;

    return {
      dailyTone: daily >= 0 ? "good" : "bad",
      allTimeTone: allTime >= 0 ? "good" : "bad",
      deployedRatio: clamp01(deployed / 100),
    };
  }, [portfolio]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between gap-3 flex-wrap">
        <div className="flex items-center gap-3">
          <div className="relative">
            <div className="absolute -inset-2 rounded-2xl bg-gradient-to-r from-[#0077ff30] to-[#00d08420] blur-lg" />
            <div className="relative p-2.5 rounded-2xl bg-white/5 border border-white/10">
              <Wallet className="w-6 h-6 text-white/70" />
            </div>
          </div>
          <div>
            <h1 className="text-3xl font-bold text-white tracking-tight">Portfolio</h1>
            <p className="text-white/50 text-sm mt-0.5">
              Modern fintech stats + mission-control realtime
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 px-2 py-1 rounded-full border border-white/10 bg-white/5">
            <span
              className={`text-xs font-mono transition-colors duration-300 ${
                liveFlash ? "text-[#00d084]" : "text-[#64748b]"
              }`}
            >
              ●
            </span>
            <span
              className={`text-xs font-mono transition-colors duration-300 ${
                liveFlash ? "text-[#00d084]" : "text-[#64748b]"
              }`}
            >
              LIVE
            </span>
          </div>

          <div className="text-[11px] font-mono text-white/40">
            Updated: {relativeTime(portfolio?.updated_at ?? null)}
          </div>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-2xl border border-red-500/30 bg-red-500/10">
          <div className="text-red-200 text-sm font-medium">Couldn’t load portfolio</div>
          <div className="text-red-200/70 text-xs mt-1 font-mono break-all">{error}</div>
          <div className="text-red-200/60 text-xs mt-2">
            Check that the Supabase project has a <code className="font-mono">portfolio</code> table and RLS allows
            authenticated reads.
          </div>
        </div>
      )}

      {/* Hero + KPIs */}
      <div className="grid grid-cols-1 xl:grid-cols-5 gap-4">
        {/* HERO */}
        <Card className="xl:col-span-3 p-5 overflow-hidden relative">
          <div className="absolute inset-0 pointer-events-none">
            <div className="absolute -top-20 -right-20 h-56 w-56 rounded-full bg-[#0077ff25] blur-3xl" />
            <div className="absolute -bottom-24 -left-24 h-64 w-64 rounded-full bg-[#00d08418] blur-3xl" />
          </div>

          <div className="relative flex items-start justify-between gap-4">
            <div>
              <div className="text-xs font-mono text-white/50 uppercase tracking-wide">Total Value</div>
              <div className="mt-2">
                {loading ? (
                  <Skeleton className="h-10 w-52" />
                ) : (
                  <div className="text-4xl md:text-5xl font-semibold text-white tracking-tight">
                    {formatUsd(portfolio?.total_value ?? 0)}
                  </div>
                )}
              </div>

              <div className="mt-3 flex flex-wrap items-center gap-2">
                <div
                  className={`px-2.5 py-1 rounded-full text-xs font-mono border ${
                    (portfolio?.daily_pnl ?? 0) >= 0
                      ? "bg-[#00d08410] border-[#00d08425] text-[#00d084]"
                      : "bg-red-500/10 border-red-500/20 text-red-300"
                  }`}
                >
                  Daily: {formatUsd(portfolio?.daily_pnl ?? 0)}
                </div>
                <div
                  className={`px-2.5 py-1 rounded-full text-xs font-mono border ${
                    (portfolio?.all_time_pnl ?? 0) >= 0
                      ? "bg-[#00d08410] border-[#00d08425] text-[#00d084]"
                      : "bg-red-500/10 border-red-500/20 text-red-300"
                  }`}
                >
                  All-time: {formatUsd(portfolio?.all_time_pnl ?? 0)}
                </div>
              </div>
            </div>

            {/* Deployed gauge */}
            <div className="w-full max-w-[220px]">
              <div className="flex items-center justify-between">
                <div className="text-xs font-mono text-white/50 uppercase tracking-wide">Deployed</div>
                <div className="text-xs font-mono text-white/70">
                  {loading ? "—" : formatPct(portfolio?.deployed_pct ?? 0)}
                </div>
              </div>
              <div className="mt-2 h-2 rounded-full bg-white/5 border border-white/10 overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-[#0077ff] to-[#00d084]"
                  style={{ width: `${Math.round((portfolio?.deployed_pct ?? 0) * 10) / 10}%` }}
                />
              </div>
              <div className="mt-2 text-[11px] text-white/40">
                Mission rule: keep deployed under your configured risk cap.
              </div>
            </div>
          </div>
        </Card>

        {/* KPI STACK */}
        <div className="xl:col-span-2 grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-1 gap-4">
          <Card className="p-4">
            <div className="flex items-center justify-between">
              <div className="text-xs font-mono text-white/50 uppercase tracking-wide">Cash</div>
              <div className="p-2 rounded-sm bg-white/5 border border-white/10">
                <Wallet className="w-4 h-4 text-white/60" />
              </div>
            </div>
            <div className="mt-3">
              {loading ? (
                <Skeleton className="h-7 w-36" />
              ) : (
                <div className="text-2xl font-semibold text-white">{formatUsd(portfolio?.cash ?? 0)}</div>
              )}
            </div>
          </Card>

          <Card className="p-4">
            <div className="flex items-center justify-between">
              <div className="text-xs font-mono text-white/50 uppercase tracking-wide">Daily PnL</div>
              <div className="p-2 rounded-sm bg-white/5 border border-white/10">
                <Activity className="w-4 h-4 text-white/60" />
              </div>
            </div>
            <div className="mt-3">
              {loading ? (
                <Skeleton className="h-7 w-36" />
              ) : (
                <div
                  className={`text-2xl font-semibold ${
                    derived?.dailyTone === "good" ? "text-[#00d084]" : "text-red-300"
                  }`}
                >
                  {formatUsd(portfolio?.daily_pnl ?? 0)}
                </div>
              )}
            </div>
          </Card>

          <Card className="p-4">
            <div className="flex items-center justify-between">
              <div className="text-xs font-mono text-white/50 uppercase tracking-wide">All-time PnL</div>
              <div className="p-2 rounded-sm bg-white/5 border border-white/10">
                <TrendingUp className="w-4 h-4 text-white/60" />
              </div>
            </div>
            <div className="mt-3">
              {loading ? (
                <Skeleton className="h-7 w-36" />
              ) : (
                <div
                  className={`text-2xl font-semibold ${
                    derived?.allTimeTone === "good" ? "text-[#00d084]" : "text-red-300"
                  }`}
                >
                  {formatUsd(portfolio?.all_time_pnl ?? 0)}
                </div>
              )}
            </div>
          </Card>

          <Card className="p-4">
            <div className="flex items-center justify-between">
              <div className="text-xs font-mono text-white/50 uppercase tracking-wide">Risk Posture</div>
              <div className="p-2 rounded-sm bg-white/5 border border-white/10">
                <Shield className="w-4 h-4 text-white/60" />
              </div>
            </div>
            <div className="mt-3">
              {loading ? (
                <Skeleton className="h-7 w-44" />
              ) : (
                <div className="text-sm text-white/80">
                  Deployed: <span className="text-white">{formatPct(portfolio?.deployed_pct ?? 0)}</span>
                  <div className="mt-1 text-[11px] text-white/40">
                    (Add max deployed + stop-loss badges next)
                  </div>
                </div>
              )}
            </div>
          </Card>
        </div>
      </div>

      {/* Footer / next */}
      <Card className="p-4">
        <div className="text-xs font-mono text-white/50 uppercase tracking-wide">Next</div>
        <div className="mt-2 text-sm text-white/70">
          Next upgrade: add a small equity sparkline by storing a daily snapshot table (portfolio_history).
        </div>
      </Card>
    </div>
  );
}
