import { createClient } from "@supabase/supabase-js";

/**
 * Server-side Supabase client for Next.js route handlers.
 *
 * NOTE:
 * - We intentionally create the client lazily (inside the handler) so `next build`
 *   does not crash when env vars are not present.
 * - For production writes, prefer a service role key (not NEXT_PUBLIC_*).
 */
export function getSupabaseAdmin() {
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const key = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

  if (!url || !key) {
    throw new Error(
      "Supabase env missing. Set NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY."
    );
  }

  return createClient(url, key, {
    auth: { persistSession: false, autoRefreshToken: false },
  });
}
