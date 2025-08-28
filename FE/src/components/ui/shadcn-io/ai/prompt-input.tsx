import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import { ComponentProps, FormEventHandler, HTMLAttributes } from 'react'
import type { ReactNode } from 'react'

export function PromptInput({ onSubmit, children }: { onSubmit: FormEventHandler<HTMLFormElement>; children: ReactNode }) {
  return (
    <form onSubmit={onSubmit} className="flex flex-col gap-2">
      {children}
    </form>
  )
}

export function PromptInputTextarea(
  props: ComponentProps<'textarea'> & { disabled?: boolean }
) {
  return (
    <textarea
      rows={3}
      className={cn(
        'w-full resize-none rounded-md border bg-background p-3 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring',
        props.className
      )}
      {...props}
    />
  )
}

export function PromptInputToolbar({ children }: { children: ReactNode }) {
  return <div className="flex items-center justify-between gap-2">{children}</div>
}

export function PromptInputTools({ children }: { children: ReactNode }) {
  return <div className="flex items-center gap-2">{children}</div>
}

export function PromptInputButton({ children, disabled }: { children: ReactNode; disabled?: boolean }) {
  return (
    <Button type="button" variant="ghost" size="sm" disabled={disabled}>
      {children}
    </Button>
  )
}

export function PromptInputSubmit({ disabled, status }: { disabled?: boolean; status?: 'ready' | 'streaming' }) {
  return (
    <Button type="submit" disabled={disabled}>
      {status === 'streaming' ? 'Sending…' : 'Send'}
    </Button>
  )
}

export function PromptInputModelSelect({ value, onValueChange, disabled, children }: { value: string; onValueChange: (v: string) => void; disabled?: boolean; children: ReactNode }) {
  return (
    <div className="relative">
      <select
        className="h-8 rounded-md border bg-background px-2 text-sm"
        value={value}
        onChange={(e) => onValueChange(e.target.value)}
        disabled={disabled}
      >
        {/* items provided in content */}
      </select>
      {children}
    </div>
  )
}

export const PromptInputModelSelectTrigger = ({ children }: { children: ReactNode }) => <>{children}</>
export const PromptInputModelSelectValue = () => null
export const PromptInputModelSelectContent = ({ children }: { children: ReactNode }) => <>{children}</>
export const PromptInputModelSelectItem = ({ value, children }: { value: string; children: ReactNode }) => (
  <option value={value}>{children}</option>
)


