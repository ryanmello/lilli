"use client"

import { useState, useCallback } from "react"

export interface Message {
  id: string
  role: "user" | "assistant"
  content: string
  timestamp: Date
  status: "sent" | "sending" | "error"
}

interface UseChatOptions {
  onError?: (error: Error) => void
}

// Simulated AI response for demo purposes
async function simulateAIResponse(userMessage: string): Promise<string> {
  await new Promise((resolve) => setTimeout(resolve, 1000 + Math.random() * 1000))
  
  const responses = [
    `I understand you're asking about "${userMessage}". Let me help you with that.\n\nHere's what I think might be useful for you...`,
    `Great question! When it comes to "${userMessage}", there are a few things to consider.\n\nFirst, let me break this down for you.`,
    `Thanks for reaching out! I'd be happy to help with "${userMessage}".\n\nHere's my take on this...`,
    `Interesting topic! "${userMessage}" is something I can definitely assist with.\n\nLet me share some thoughts.`,
  ]
  
  return responses[Math.floor(Math.random() * responses.length)]
}

export function useChat(options: UseChatOptions = {}) {
  const [messages, setMessages] = useState<Message[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [isStreaming, setIsStreaming] = useState(false)
  const [streamingContent, setStreamingContent] = useState("")
  const [error, setError] = useState<string | null>(null)

  const sendMessage = useCallback(
    async (content: string) => {
      const userMessage: Message = {
        id: `user-${Date.now()}`,
        role: "user",
        content,
        timestamp: new Date(),
        status: "sent",
      }

      setMessages((prev) => [...prev, userMessage])
      setIsLoading(true)
      setError(null)

      try {
        // Simulate typing delay
        await new Promise((resolve) => setTimeout(resolve, 500))
        setIsLoading(false)
        setIsStreaming(true)

        // Get AI response
        const response = await simulateAIResponse(content)

        // Simulate streaming effect
        let currentContent = ""
        for (let i = 0; i < response.length; i++) {
          currentContent += response[i]
          setStreamingContent(currentContent)
          await new Promise((resolve) => setTimeout(resolve, 15))
        }

        const assistantMessage: Message = {
          id: `assistant-${Date.now()}`,
          role: "assistant",
          content: response,
          timestamp: new Date(),
          status: "sent",
        }

        setMessages((prev) => [...prev, assistantMessage])
        setStreamingContent("")
        setIsStreaming(false)
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : "An error occurred"
        setError(errorMessage)
        setIsLoading(false)
        setIsStreaming(false)
        setStreamingContent("")
        options.onError?.(err instanceof Error ? err : new Error(errorMessage))
      }
    },
    [options]
  )

  const regenerate = useCallback(async () => {
    const lastUserMessage = [...messages].reverse().find((m) => m.role === "user")
    if (!lastUserMessage) return

    // Remove the last assistant message
    setMessages((prev) => {
      const lastAssistantIndex = prev.findLastIndex((m) => m.role === "assistant")
      if (lastAssistantIndex >= 0) {
        return prev.slice(0, lastAssistantIndex)
      }
      return prev
    })

    // Resend the last user message
    setIsLoading(true)
    setError(null)

    try {
      await new Promise((resolve) => setTimeout(resolve, 500))
      setIsLoading(false)
      setIsStreaming(true)

      const response = await simulateAIResponse(lastUserMessage.content)

      let currentContent = ""
      for (let i = 0; i < response.length; i++) {
        currentContent += response[i]
        setStreamingContent(currentContent)
        await new Promise((resolve) => setTimeout(resolve, 15))
      }

      const assistantMessage: Message = {
        id: `assistant-${Date.now()}`,
        role: "assistant",
        content: response,
        timestamp: new Date(),
        status: "sent",
      }

      setMessages((prev) => [...prev, assistantMessage])
      setStreamingContent("")
      setIsStreaming(false)
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "An error occurred"
      setError(errorMessage)
      setIsLoading(false)
      setIsStreaming(false)
      setStreamingContent("")
    }
  }, [messages])

  const clearMessages = useCallback(() => {
    setMessages([])
    setError(null)
    setStreamingContent("")
    setIsStreaming(false)
    setIsLoading(false)
  }, [])

  const exportConversation = useCallback(() => {
    const content = messages
      .map((m) => `[${m.role.toUpperCase()}] ${m.content}`)
      .join("\n\n")
    
    const blob = new Blob([content], { type: "text/plain" })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = `lilli-conversation-${new Date().toISOString().split("T")[0]}.txt`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }, [messages])

  return {
    messages,
    isLoading,
    isStreaming,
    streamingContent,
    error,
    sendMessage,
    regenerate,
    clearMessages,
    exportConversation,
  }
}
