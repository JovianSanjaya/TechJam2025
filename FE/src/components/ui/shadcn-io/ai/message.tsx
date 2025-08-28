import { cn } from '@/lib/utils'
import { HTMLAttributes } from 'react'

export function Message({ from, className, ...props }: HTMLAttributes<HTMLDivElement> & { from: 'user' | 'assistant' }) {
  return (
    <div
      className={cn(
        'flex items-start gap-3',
        from === 'user' ? 'justify-end' : 'justify-start',
        className
      )}
      {...props}
    />
  )
}

export function MessageAvatar({ src, name }: { src?: string; name?: string }) {
  return <img src={src} alt={name} className="h-6 w-6 rounded-full border" />
}

export function MessageContent({ className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        'max-w-[80%] rounded-lg border bg-card px-3 py-2 text-sm shadow-sm',
        className
      )}
      {...props}
    />
  )
}


