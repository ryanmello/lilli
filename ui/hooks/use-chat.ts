"use client"

import { useState, useCallback } from "react"

const API_BASE_URL = "http://localhost:8000/api"

export interface Message {
  id: string
  role: "user" | "assistant"
  content: string
  timestamp: Date
  status: "sent" | "sending" | "error"
  agentName?: string
}

interface UseChatOptions {
  onError?: (error: Error) => void
}

interface AIResponse {
  output: Record<string, unknown>  // Structured output from agent
  agent_name: string
  error: string
}

function formatOutput(output: Record<string, unknown>): string {
  // Format structured output for display
  if (output.query && output.explanation) {
    return `**SQL Query:**\n\`\`\`sql\n${output.query}\n\`\`\`\n\n**Explanation:** ${output.explanation}`
  }
  // Fallback: format as JSON
  return JSON.stringify(output, null, 2)
}

async function sendToAPI(userMessage: string): Promise<AIResponse> {
  const response = await fetch(`${API_BASE_URL}/process_request`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ input: userMessage }),
  })

  if (!response.ok) {
    throw new Error(`API error: ${response.status} ${response.statusText}`)
  }

  return response.json()
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
        // Get AI response from API
        const apiResponse = await sendToAPI(content)

        if (apiResponse.error) {
          throw new Error(apiResponse.error)
        }

        setIsLoading(false)
        setIsStreaming(true)

        const formattedOutput = formatOutput(apiResponse.output)

        // Simulate streaming effect for better UX
        let currentContent = ""
        for (let i = 0; i < formattedOutput.length; i++) {
          currentContent += formattedOutput[i]
          setStreamingContent(currentContent)
          await new Promise((resolve) => setTimeout(resolve, 15))
        }

        const assistantMessage: Message = {
          id: `assistant-${Date.now()}`,
          role: "assistant",
          content: formattedOutput,
          timestamp: new Date(),
          status: "sent",
          agentName: apiResponse.agent_name,
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
      const apiResponse = await sendToAPI(lastUserMessage.content)

      if (apiResponse.error) {
        throw new Error(apiResponse.error)
      }

      setIsLoading(false)
      setIsStreaming(true)

      const formattedOutput = formatOutput(apiResponse.output)

      let currentContent = ""
      for (let i = 0; i < formattedOutput.length; i++) {
        currentContent += formattedOutput[i]
        setStreamingContent(currentContent)
        await new Promise((resolve) => setTimeout(resolve, 15))
      }

      const assistantMessage: Message = {
        id: `assistant-${Date.now()}`,
        role: "assistant",
        content: formattedOutput,
        timestamp: new Date(),
        status: "sent",
        agentName: apiResponse.agent_name,
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
