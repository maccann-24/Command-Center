import { createClient } from "@supabase/supabase-js"

/**
 * Browser/client Supabase instance.
 *
 * IMPORTANT:
 * - In Vercel/runtime you must set NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY.
 * - During `next build`, env may be missing in CI/local shells.
 *   To avoid build-time crashes, we fall back to a dummy local URL/key.
 */
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || "http://localhost:54321"
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || "anon"

export const supabase = createClient(supabaseUrl, supabaseAnonKey)
