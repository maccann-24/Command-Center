import { getEvents } from "@/lib/supabase/trading"
import EventLog from "../components/EventLog"

export default async function EventsPage() {
  // Fetch last 100 events
  const events = await getEvents({ limit: 100 })

  return (
    <div className="p-8 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">Event Log</h1>
        <p className="text-muted-foreground mt-1">
          Full audit trail of all trading system events
        </p>
      </div>

      {/* Event Log */}
      <EventLog initialEvents={events} />
    </div>
  )
}
