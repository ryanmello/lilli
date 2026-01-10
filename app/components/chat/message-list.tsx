"use client"

import { useEffect, useRef } from "react"
import { MessageBubble } from "./message-bubble"

export interface Message {
  id: string
  role: "user" | "assistant"
  content: string
  timestamp: Date
  status: "sending" | "sent" | "error"
}

interface MessageListProps {
  messages: Message[]
  isStreaming?: boolean
  streamingContent?: string
  onRegenerate?: () => void
}

export function MessageList({
  messages,
  isStreaming,
  streamingContent,
  onRegenerate,
}: MessageListProps) {
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages, streamingContent])

  return (
    <div className="flex flex-col py-4">
      {messages.map((message, index) => (
        <MessageBubble
          key={message.id}
          role={message.role}
          content={message.content}
          timestamp={message.timestamp}
          onRegenerate={
            message.role === "assistant" && index === messages.length - 1
              ? onRegenerate
              : undefined
          }
        />
      ))}

      {/* Streaming message */}
      {isStreaming && streamingContent && (
        <MessageBubble
          role="assistant"
          content={streamingContent}
          isStreaming={true}
        />
      )}

      <div ref={bottomRef} />
    </div>
  )
}
