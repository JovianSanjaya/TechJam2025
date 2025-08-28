import { useState } from 'react'
import { Button } from '@/components/ui/button'

export function Reasoning({ isStreaming, defaultOpen = false, children }: { isStreaming?: boolean; defaultOpen?: boolean; children: React.ReactNode }) {
  const [open, setOpen] = useState(defaultOpen)
  return (
    <div className="rounded-md border bg-muted/30 p-3 text-sm">
      {open && <ReasoningContent>{children}</ReasoningContent>}
      <div className="mt-2">
        <ReasoningTrigger onClick={() => setOpen(!open)} />
      </div>
    </div>
  )
}

export function ReasoningTrigger() {
  return <Button size="sm" variant="ghost">Reasoning</Button>
}

export function ReasoningContent({ children }: { children: React.ReactNode }) {
  return <div className="text-muted-foreground">{children}</div>
}


