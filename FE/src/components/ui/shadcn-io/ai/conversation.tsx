import { cn } from '@/lib/utils'
import { HTMLAttributes, forwardRef } from 'react'
import { ChevronDown } from 'lucide-react'

export const Conversation = ({ className, ...props }: HTMLAttributes<HTMLDivElement>) => {
  return <div className={cn('flex flex-col', className)} {...props} />
}

export const ConversationContent = ({ className, ...props }: HTMLAttributes<HTMLDivElement>) => {
  return <div className={cn('flex flex-col gap-4 p-4', className)} {...props} />
}

export const ConversationScrollButton = forwardRef<HTMLButtonElement, HTMLAttributes<HTMLButtonElement>>(function ScrollBtn(
  { className, ...props },
  ref
) {
  return (
    <button
      ref={ref}
      className={cn(
        'inline-flex h-10 w-10 items-center justify-center rounded-full bg-foreground text-background shadow transition-opacity hover:opacity-90',
        className
      )}
      aria-label="Scroll to bottom"
      {...(props as any)}
    >
      <ChevronDown className="h-5 w-5" />
    </button>
  )
})


