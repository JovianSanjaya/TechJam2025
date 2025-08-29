import {
  Conversation,
  ConversationContent,
  ConversationScrollButton,
} from '@/components/ui/shadcn-io/ai/conversation'
import { Loader } from '@/components/ui/shadcn-io/ai/loader'
import { Message, MessageContent } from '@/components/ui/shadcn-io/ai/message'
import {
  PromptInput,
  PromptInputButton,
  PromptInputSubmit,
  PromptInputTextarea,
  PromptInputToolbar,
  PromptInputTools,
} from '@/components/ui/shadcn-io/ai/prompt-input'
import {
  Reasoning,
  ReasoningContent,
  ReasoningTrigger,
} from '@/components/ui/shadcn-io/ai/reasoning'
// Sources UI removed
import { Button } from '@/components/ui/button'
import { Mic, Paperclip, RotateCcw } from 'lucide-react'
import { nanoid } from 'nanoid'
import { type FormEventHandler, useCallback, useEffect, useRef, useState } from 'react'

type ChatMessage = {
  id: string
  content: string
  role: 'user' | 'assistant'
  timestamp: Date
  reasoning?: string
  isStreaming?: boolean
}

// Removed model selection UI

const sampleResponses = [
  {
    content:
      "I'd be happy to help you with that! React is a powerful JavaScript library for building user interfaces. What specific aspect would you like to explore?",
    reasoning:
      'The user is asking about React, which is a broad topic. I should provide a helpful overview while asking for more specific information to give a more targeted response.',
  },
  {
    content:
      'Next.js is an excellent framework built on top of React that provides server-side rendering, static site generation, and many other powerful features out of the box.',
    reasoning:
      'The user mentioned Next.js, so I should explain its relationship to React and highlight its key benefits for modern web development.',
  },
  {
    content:
      "TypeScript adds static type checking to JavaScript, which helps catch errors early and improves code quality. It's particularly valuable in larger applications.",
    reasoning:
      "TypeScript is becoming increasingly important in modern development. I should explain its benefits while keeping the explanation accessible.",
  },
]

export function Chat() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: nanoid(),
      content:
        "Hello! I'm your AI assistant. I can help you with coding questions, explain concepts, and provide guidance on web development topics. What would you like to know?",
      role: 'assistant',
      timestamp: new Date(),
    },
  ])

  const [inputValue, setInputValue] = useState('')
  // Removed model selection state
  const [isTyping, setIsTyping] = useState(false)
  const [streamingMessageId, setStreamingMessageId] = useState<string | null>(null)

  const simulateTyping = useCallback(
    (messageId: string, content: string, reasoning?: string) => {
      let currentIndex = 0
      const typeInterval = setInterval(() => {
        setMessages((prev) =>
          prev.map((msg) => {
            if (msg.id === messageId) {
              const currentContent = content.slice(0, currentIndex)
              return {
                ...msg,
                content: currentContent,
                isStreaming: currentIndex < content.length,
                reasoning: currentIndex >= content.length ? reasoning : undefined,
              }
            }
            return msg
          })
        )

        // Faster typing: bigger steps and shorter interval
        currentIndex += Math.random() > 0.2 ? 3 : 1

        if (currentIndex >= content.length) {
          clearInterval(typeInterval)
          setIsTyping(false)
          setStreamingMessageId(null)
        }
      }, 24)

      return () => clearInterval(typeInterval)
    },
    []
  )

  const handleSubmit: FormEventHandler<HTMLFormElement> = useCallback(
    (event) => {
      event.preventDefault()

      if (!inputValue.trim() || isTyping) return

      const userMessage: ChatMessage = {
        id: nanoid(),
        content: inputValue.trim(),
        role: 'user',
        timestamp: new Date(),
      }

      setMessages((prev) => [...prev, userMessage])
      setInputValue('')
      setIsTyping(true)

      setTimeout(() => {
        const responseData =
          sampleResponses[Math.floor(Math.random() * sampleResponses.length)]
        const assistantMessageId = nanoid()

        const assistantMessage: ChatMessage = {
          id: assistantMessageId,
          content: '',
          role: 'assistant',
          timestamp: new Date(),
          isStreaming: true,
        }

        setMessages((prev) => [...prev, assistantMessage])
        setStreamingMessageId(assistantMessageId)

        simulateTyping(assistantMessageId, responseData.content, responseData.reasoning)
      }, 800)
    },
    [inputValue, isTyping, simulateTyping]
  )

  const handleReset = useCallback(() => {
    setMessages([
      {
        id: nanoid(),
        content:
          "Hello! I'm your AI assistant. I can help you with coding questions, explain concepts, and provide guidance on web development topics. What would you like to know?",
        role: 'assistant',
        timestamp: new Date(),
      },
    ])
    setInputValue('')
    setIsTyping(false)
    setStreamingMessageId(null)
  }, [])

  const scrollRef = useRef<HTMLDivElement | null>(null)
  const [showScrollBtn, setShowScrollBtn] = useState(false)

  const scrollToBottom = useCallback(() => {
    const el = scrollRef.current
    if (!el) return
    el.scrollTo({ top: el.scrollHeight, behavior: 'smooth' })
  }, [])

  useEffect(() => {
    const el = scrollRef.current
    if (!el) return
    const onScroll = () => {
      const atBottom = el.scrollHeight - el.scrollTop - el.clientHeight < 32
      setShowScrollBtn(!atBottom)
    }
    el.addEventListener('scroll', onScroll, { passive: true } as any)
    // initialize
    onScroll()
    return () => el.removeEventListener('scroll', onScroll)
  }, [])

  useEffect(() => {
    if (!showScrollBtn) {
      scrollToBottom()
    }
  }, [messages, showScrollBtn, scrollToBottom])

  return (
    <div className="flex h-[85vh] w-full flex-col overflow-hidden rounded-xl border bg-background shadow-sm">
  {/* Header */}
  <div className="flex items-center justify-between border-b bg-muted/50 px-4 py-3">
    <div className="flex items-center gap-2">
      <div className="h-2 w-2 rounded-full bg-green-500" />
      <span className="text-sm font-medium">AI Assistant</span>
    </div>
    <Button variant="ghost" size="sm" onClick={handleReset} className="h-8 px-2">
      <RotateCcw className="h-4 w-4" />
      <span className="ml-1">Reset</span>
    </Button>
  </div>

  {/* Conversation area (scrollable) */}
  <div className="flex-1 overflow-y-auto">
    <Conversation className="relative flex flex-col h-full">
      <ConversationContent className="space-y-4 px-4 py-3">
        {messages.map((message) => (
          <div key={message.id} className="space-y-3">
            <Message from={message.role}>
              <MessageContent>
                {message.isStreaming && message.content === '' ? (
                  <div className="flex items-center gap-2">
                    <Loader size={14} />
                    <span className="text-sm text-muted-foreground">Thinking...</span>
                  </div>
                ) : (
                  message.content
                )}
              </MessageContent>
            </Message>

            {message.reasoning && (
              <div className="ml-10">
                <Reasoning isStreaming={message.isStreaming} defaultOpen={false}>
                  <ReasoningTrigger />
                  <ReasoningContent>{message.reasoning}</ReasoningContent>
                </Reasoning>
              </div>
            )}
          </div>
        ))}
      </ConversationContent>

      {showScrollBtn && messages.length > 2 && (
        <ConversationScrollButton
          onClick={scrollToBottom}
          className="absolute bottom-4 right-4"
        />
      )}
    </Conversation>
  </div>

  {/* Input bar (sticky at bottom) */}
  <div className="border-t p-4 bg-background sticky bottom-0">
    <PromptInput onSubmit={handleSubmit}>
      <PromptInputTextarea
        value={inputValue}
        onChange={(e) => setInputValue(e.target.value)}
        placeholder="Ask me anything about development, coding, or technology..."
        disabled={isTyping}
      />
      <PromptInputToolbar>
        <PromptInputTools>
          <PromptInputButton disabled={isTyping}>
            <Paperclip className="h-4 w-4" />
          </PromptInputButton>
          <PromptInputButton disabled={isTyping}>
            <Mic className="h-4 w-4" />
            <span>Voice</span>
          </PromptInputButton>
        </PromptInputTools>
        <PromptInputSubmit
          disabled={!inputValue.trim() || isTyping}
          status={isTyping ? 'streaming' : 'ready'}
        />
      </PromptInputToolbar>
    </PromptInput>
  </div>
</div>

    
  )
}


