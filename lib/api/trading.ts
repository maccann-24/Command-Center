/**
 * FastAPI Trading Bot Client
 * Functions for interacting with the trading bot's FastAPI endpoints
 */

const FASTAPI_BASE_URL = process.env.NEXT_PUBLIC_FASTAPI_URL || "http://localhost:8000"

export type BotHealth = {
  status: "healthy" | "degraded" | "offline"
  healthy?: boolean
  last_cycle_time?: string
  uptime_seconds?: number
  mode?: "paper" | "live"
}

export type BotStatus = {
  running: boolean
  mode: "paper" | "live"
  uptime_seconds: number
  last_cycle_time: string
  next_cycle_eta_seconds?: number
  positions_count?: number
  theses_count?: number
  portfolio_value?: number
}

/**
 * Get bot health status
 */
export async function getBotHealth(): Promise<BotHealth | null> {
  try {
    const res = await fetch(`${FASTAPI_BASE_URL}/health`, {
      method: "GET",
      headers: { "Content-Type": "application/json" },
      cache: "no-store",
    })

    if (!res.ok) {
      return { status: "offline" }
    }

    const data = await res.json()

    if (data.status === "healthy" || data.healthy === true) {
      return {
        status: "healthy",
        healthy: true,
        last_cycle_time: data.last_cycle_time,
        uptime_seconds: data.uptime_seconds,
        mode: data.mode,
      }
    }

    return { status: "degraded" }
  } catch (error) {
    console.error("Failed to fetch bot health:", error)
    return { status: "offline" }
  }
}

/**
 * Get detailed bot status
 */
export async function getBotStatus(): Promise<BotStatus | null> {
  try {
    const res = await fetch(`${FASTAPI_BASE_URL}/status`, {
      method: "GET",
      headers: { "Content-Type": "application/json" },
      cache: "no-store",
    })

    if (!res.ok) {
      return null
    }

    const data = await res.json()
    return data as BotStatus
  } catch (error) {
    console.error("Failed to fetch bot status:", error)
    return null
  }
}

/**
 * Emergency stop the bot
 */
export async function emergencyStop(): Promise<{ success: boolean; message?: string }> {
  try {
    const res = await fetch(`${FASTAPI_BASE_URL}/stop`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
    })

    if (!res.ok) {
      return {
        success: false,
        message: `HTTP error: ${res.status}`,
      }
    }

    const data = await res.json()
    return {
      success: true,
      message: data.message || "Bot stopped successfully",
    }
  } catch (error) {
    console.error("Failed to stop bot:", error)
    return {
      success: false,
      message: error instanceof Error ? error.message : "Unknown error",
    }
  }
}
