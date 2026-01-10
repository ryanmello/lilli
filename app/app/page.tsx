"use client";

import { ChatInput } from "@/components/chat/chat-input";
import { MessageList } from "@/components/chat/message-list";
import { TypingIndicator } from "@/components/chat/typing-indicator";
import { WelcomeScreen } from "@/components/chat/welcome-screen";
import { useChat } from "@/hooks/use-chat";

export default function ChatPage() {
  const {
    messages,
    isLoading,
    isStreaming,
    streamingContent,
    sendMessage,
    regenerate,
    clearMessages,
    exportConversation,
  } = useChat();

  return (
    <div className="flex flex-col h-screen bg-background">
      <main className="flex-1 overflow-hidden flex flex-col">
        {/* Scrollable message area */}
        <div className="flex-1 overflow-y-auto scrollbar-thin">
          <div className="max-w-3xl mx-auto">
            {messages.length === 0 && !isLoading && !isStreaming ? (
              <WelcomeScreen />
            ) : (
              <>
                <MessageList
                  messages={messages}
                  isStreaming={isStreaming}
                  streamingContent={streamingContent}
                  onRegenerate={regenerate}
                />
                {isLoading && !isStreaming && <TypingIndicator />}
              </>
            )}
          </div>
        </div>

        {/* Fixed input area */}
        <ChatInput onSend={sendMessage} disabled={isLoading || isStreaming} />
      </main>
    </div>
  );
}
