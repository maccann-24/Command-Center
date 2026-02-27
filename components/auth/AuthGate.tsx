"use client";

import { useEffect, useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import { supabase } from "@/lib/supabase";

/**
 * Client-side auth gate for the dashboard.
 *
 * Notes:
 * - Uses Supabase Auth session stored in the browser.
 * - Redirects unauthenticated users to /login.
 */
export function AuthGate({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const [ready, setReady] = useState(false);
  const [authed, setAuthed] = useState(false);

  const isPublicRoute = pathname === "/login";

  useEffect(() => {
    let mounted = true;

    async function init() {
      const { data } = await supabase.auth.getSession();
      if (!mounted) return;
      const hasSession = !!data.session;
      setAuthed(hasSession);
      setReady(true);
      if (!hasSession && !isPublicRoute) router.replace("/login");
      if (hasSession && isPublicRoute) router.replace("/");
    }

    init();

    const { data: sub } = supabase.auth.onAuthStateChange((_event, session) => {
      const hasSession = !!session;
      setAuthed(hasSession);
      if (!hasSession && !isPublicRoute) router.replace("/login");
      if (hasSession && isPublicRoute) router.replace("/");
    });

    return () => {
      mounted = false;
      sub.subscription.unsubscribe();
    };
  }, [router, isPublicRoute]);

  // Always allow login page to render (it will redirect away if already authed).
  if (isPublicRoute) return <>{children}</>;

  // Prevent rendering protected routes before we know auth status.
  if (!ready) {
    return (
      <div className="min-h-[50vh] flex items-center justify-center">
        <div className="text-xs font-mono text-white/60">Checking session…</div>
      </div>
    );
  }

  if (!authed) return null;

  return <>{children}</>;
}
