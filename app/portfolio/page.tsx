"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { supabase } from "@/lib/supabase";
import { Card } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Wallet, TrendingUp, Shield, Activity } from "lucide-react";

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

  const stats = useMemo(() => {
    if (!portfolio) return null;
    return [
      {
        label: "Cash",
        value: formatUsd(portfolio.cash ?? 0),
        icon: Wallet,
      },
      {
        label: "Total Value",
        value: formatUsd(portfolio.total_value ?? 0),
        icon: TrendingUp,
      },
      {
        label: "Deployed",
        value: formatPct(portfolio.deployed_pct ?? 0),
        icon: Shield,
      },
      {
        label: "Daily PnL",
        value: formatUsd(portfolio.daily_pnl ?? 0),
        icon: Activity,
        tone: (portfolio.daily_pnl ?? 0) >= 0 ? "good" : "bad",
      },
    ] as const;
  }, [portfolio]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between gap-3 flex-wrap">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-white/5 border border-white/10">
            <Wallet className="w-6 h-6 text-white/70" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-white">Portfolio</h1>
            <p className="text-white/50 text-sm mt-0.5">Realtime view (Supabase)</p>
          </div>
        </div>

        <div className="flex items-center gap-2 px-2 py-1">
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
      </div>

      {error && (
        <div className="p-4 rounded-2xl border border-red-500/30 bg-red-500/10">
          <div className="text-red-200 text-sm font-medium">Couldn’t load portfolio</div>
          <div className="text-red-200/70 text-xs mt-1 font-mono break-all">{error}</div>
          <div className="text-red-200/60 text-xs mt-2">
            Check that your Supabase project has a <code className="font-mono">portfolio</code> table and that RLS policies allow
            authenticated reads.
          </div>
        </div>
      )}

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        {loading &&
          Array.from({ length: 4 }).map((_, i) => (
            <Card key={i} className="p-4">
              <div className="flex items-center justify-between">
                <Skeleton className="h-4 w-24" />
                <Skeleton className="h-8 w-8" />
              </div>
              <div className="mt-3">
                <Skeleton className="h-7 w-36" />
              </div>
            </Card>
          ))}

        {!loading && stats &&
          stats.map((s) => {
            const Icon = s.icon;
            const tone = (s as any).tone as "good" | "bad" | undefined;
            const valueClass =
              tone === "good" ? "text-[#00d084]" : tone === "bad" ? "text-red-300" : "text-white";

            return (
              <Card key={s.label} className="p-4">
                <div className="flex items-center justify-between">
                  <div className="text-xs font-mono text-white/50 uppercase tracking-wide">{s.label}</div>
                  <div className="p-2 rounded-sm bg-white/5 border border-white/10">
                    <Icon className="w-4 h-4 text-white/60" />
                  </div>
                </div>
                <div className={`mt-3 text-2xl font-semibold ${valueClass}`}>{s.value}</div>
              </Card>
            );
          })}
      </div>

      {/* Detail card */}
      <Card className="p-4">
        <div className="text-xs font-mono text-white/50 uppercase tracking-wide">Details</div>
        {loading ? (
          <div className="mt-3 space-y-2">
            <Skeleton className="h-4 w-64" />
            <Skeleton className="h-4 w-56" />
          </div>
        ) : portfolio ? (
          <div className="mt-3 grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
            <div className="text-white/80">
              <span className="text-white/50">All-time PnL:</span> {formatUsd(portfolio.all_time_pnl ?? 0)}
            </div>
            <div className="text-white/80">
              <span className="text-white/50">Updated at:</span> {portfolio.updated_at ?? "—"}
            </div>
          </div>
        ) : (
          <div className="mt-3 text-sm text-white/60">No portfolio row found.</div>
        )}
      </Card>
    </div>
  );
}
