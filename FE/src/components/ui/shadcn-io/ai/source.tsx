export function Sources({ children }: { children: React.ReactNode }) {
  return <div className="text-sm">{children}</div>
}

export function SourcesTrigger({ count }: { count: number }) {
  return <div className="text-xs text-muted-foreground">Used {count} sources</div>
}

export function SourcesContent({ children }: { children: React.ReactNode }) {
  return <div className="mt-2 space-y-1">{children}</div>
}

export function Source({ href, title }: { href: string; title: string }) {
  return (
    <a href={href} target="_blank" rel="noreferrer" className="block text-blue-600 underline">
      {title}
    </a>
  )
}


