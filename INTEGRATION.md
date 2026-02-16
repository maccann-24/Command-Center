# Clawdbot Integration

Mission Control automatically tracks Clawdbot API usage costs via hourly cron job.

## Live Dashboard
https://command-center-dm3n.vercel.app

## How It Works
1. Script runs every hour on gateway: `/home/ubuntu/scripts/clawdbot-logger.sh`
2. Reads token usage from `clawdbot status`
3. Calculates NEW tokens since last run
4. POSTs to API: `/api/metrics`
5. Dashboard updates automatically

## Cost Calculation
~$10 per 1M tokens (Claude Sonnet 4 average)

## Testing
Run manually on gateway: `~/scripts/clawdbot-logger.sh`
