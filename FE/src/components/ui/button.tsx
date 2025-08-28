import { cn } from '@/lib/utils'
import { ButtonHTMLAttributes } from 'react'

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: 'default' | 'ghost'
  size?: 'sm' | 'md'
}

export function Button({ className, variant = 'default', size = 'md', ...props }: ButtonProps) {
  return (
    <button
      className={cn(
        'inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50',
        variant === 'ghost'
          ? 'bg-transparent hover:bg-muted/60'
          : 'bg-foreground text-background hover:opacity-90',
        size === 'sm' ? 'h-8 px-2' : 'h-10 px-4',
        className
      )}
      {...props}
    />
  )
}


