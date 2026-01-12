"use client"

import { useState, useRef, useEffect } from "react"
import {
  InputGroup,
  InputGroupTextarea,
  InputGroupAddon,
  InputGroupButton,
} from "@/components/ui/input-group"
import { SendHorizontal, Loader2 } from "lucide-react"

interface ChatInputProps {
  onSend: (message: string) => void
  disabled?: boolean
}

export function ChatInput({ onSend, disabled }: ChatInputProps) {
  const [message, setMessage] = useState("")
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const handleSubmit = () => {
    if (message.trim() && !disabled) {
      onSend(message.trim())
      setMessage("")
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSubmit()
    }
  }

  useEffect(() => {
    if (!disabled && textareaRef.current) {
      textareaRef.current.focus()
    }
  }, [disabled])

  return (
    <div className="p-4">
      <div className="max-w-3xl mx-auto">
        <InputGroup className="h-auto min-h-12">
          <InputGroupTextarea
            ref={textareaRef}
            placeholder="Message Lilli..."
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            className="min-h-6 max-h-32 py-3 scrollbar-textarea"
            rows={1}
            disabled={disabled}
            // Disable Grammarly and other extensions
            data-gramm="false"
            data-gramm_editor="false"
            data-enable-grammarly="false"
            spellCheck={false}
            autoComplete="off"
            autoCorrect="off"
            autoCapitalize="off"
          />

          <InputGroupAddon align="inline-end" className="self-end pb-2 cursor-pointer">
            <InputGroupButton
              onClick={handleSubmit}
              disabled={!message.trim() || disabled}
              variant={message.trim() ? "default" : "ghost"}
              size="icon-sm"
              className="transition-colors"
            >
              {disabled ? (
                <Loader2 className="size-5 animate-spin" />
              ) : (
                <SendHorizontal className="size-5" />
              )}
            </InputGroupButton>
          </InputGroupAddon>
        </InputGroup>
      </div>
    </div>
  )
}
