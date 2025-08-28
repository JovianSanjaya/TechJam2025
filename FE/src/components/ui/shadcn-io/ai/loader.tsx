export function Loader({ size = 16 }: { size?: number }) {
  return (
    <div
      style={{ width: size, height: size }}
      className="inline-block animate-pulse rounded-full bg-muted-foreground/50"
    />
  )
}


