"use client"

import { useState } from "react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Copy, RotateCcw, Check, Sparkles, User } from "lucide-react"
import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"

interface MessageBubbleProps {
  role: "user" | "assistant"
  content: string
  timestamp?: Date
  isStreaming?: boolean
  onRegenerate?: () => void
}

function formatTime(date: Date): string {
  return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
}

export function MessageBubble({
  role,
  content,
  timestamp,
  isStreaming,
  onRegenerate,
}: MessageBubbleProps) {
  const isUser = role === "user"
  const [copied, setCopied] = useState(false)

  const handleCopy = async () => {
    await navigator.clipboard.writeText(content)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div
      className={cn(
        "group flex gap-3 py-3",
        isUser ? "justify-end" : "justify-start"
      )}
    >
      {/* Avatar for assistant */}
      {!isUser && (
        <div className="size-8 rounded-full bg-primary/10 flex items-center justify-center shrink-0">
          <Sparkles className="size-4 text-primary" />
        </div>
      )}

      <div
        className={cn(
          "flex flex-col gap-1 max-w-[80%]",
          isUser && "items-end"
        )}
      >
        {/* Message content */}
        <div
          className={cn(
            "rounded-2xl px-4 py-2.5 text-sm leading-relaxed",
            isUser
              ? "bg-primary text-primary-foreground rounded-br-md whitespace-pre-wrap"
              : "bg-muted text-foreground rounded-bl-md markdown-content"
          )}
        >
          {isUser ? (
            content
          ) : (
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
          )}
          {isStreaming && (
            <span className="inline-block w-1.5 h-4 bg-current ml-1 animate-pulse" />
          )}
        </div>

        {/* Message actions (assistant only) */}
        {!isUser && !isStreaming && (
          <div className="flex items-center gap-1">
            <Button
              variant="ghost"
              size="icon-xs"
              onClick={handleCopy}
              aria-label="Copy message"
            >
              {copied ? (
                <Check className="size-3 text-green-500" />
              ) : (
                <Copy className="size-3" />
              )}
            </Button>
            {onRegenerate && (
              <Button
                variant="ghost"
                size="icon-xs"
                onClick={onRegenerate}
                aria-label="Regenerate response"
              >
                <RotateCcw className="size-3" />
              </Button>
            )}
          </div>
        )}

        {/* Timestamp */}
        {timestamp && (
          <span className="text-[0.625rem] text-muted-foreground">
            {formatTime(timestamp)}
          </span>
        )}
      </div>

      {/* User avatar */}
      {isUser && (
        <div className="size-8 rounded-full bg-secondary flex items-center justify-center shrink-0">
          <User className="size-4 text-secondary-foreground" />
        </div>
      )}
    </div>
  )
}
