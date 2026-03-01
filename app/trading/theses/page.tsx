import { getTheses } from "@/lib/supabase/trading"
import ThesisTable from "../components/ThesisTable"

export default async function ThesesPage() {
  // Fetch all theses (filtering will be done client-side)
  const theses = await getTheses({ limit: 500 })

  return (
    <div className="p-8 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">Theses</h1>
        <p className="text-muted-foreground mt-1">
          AI-generated trade opportunities with edge analysis
        </p>
      </div>

      {/* Thesis Table */}
      <ThesisTable theses={theses} />
    </div>
  )
}
