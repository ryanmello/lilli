"use client"

import { Sparkles } from "lucide-react"

export function TypingIndicator() {
  return (
    <div className="flex gap-3 px-4 py-3">
      <div className="size-8 rounded-full bg-primary/10 flex items-center justify-center shrink-0">
        <Sparkles className="size-4 text-primary" />
      </div>
      <div className="bg-muted rounded-2xl rounded-bl-md px-4 py-3 flex items-center gap-1.5">
        <span className="size-2 bg-muted-foreground/50 rounded-full animate-bounce [animation-delay:-0.3s]" />
        <span className="size-2 bg-muted-foreground/50 rounded-full animate-bounce [animation-delay:-0.15s]" />
        <span className="size-2 bg-muted-foreground/50 rounded-full animate-bounce" />
      </div>
    </div>
  )
}
