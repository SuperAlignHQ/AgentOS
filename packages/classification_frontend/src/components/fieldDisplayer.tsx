import type * as React from "react"
import { cn } from "@/lib/utils"

interface FieldDisplayProps {
  value?: React.ReactNode
  className?: string
  lines?: number // optional hint for height
}

export function FieldDisplay({ value, className, lines = 4 }: FieldDisplayProps) {
  // compute a reasonable min height from lines
  const minHeightClass = lines >= 5 ? "min-h-40" : lines === 4 ? "min-h-32" : lines === 3 ? "min-h-24" : "min-h-20"

  return (
    <div
      role="textbox"
      aria-readonly="true"
      className={cn(
        "rounded-lg border bg-card/50 px-4 py-3 text-base md:text-lg leading-relaxed",
        minHeightClass,
        className,
      )}
    >
      {value ? <span className="text-foreground">{value}</span> : <span className="text-muted-foreground">{"—"}</span>}
    </div>
  )
}
