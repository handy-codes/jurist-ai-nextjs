"use client";

import { useState, useRef, useEffect } from "react";
import { useUser } from "@clerk/nextjs";
import { Message } from "@/types/chat";
import { ChatMessage } from "./ChatMessage";
import { ChatInput } from "./ChatInput";
// import { FeedbackSection } from './FeedbackSection'
import { useChatStore } from "@/hooks/useChatStore";
import { LoadingSpinner } from "@/components/ui/LoadingSpinner";

export function ChatInterface() {
  const { user } = useUser();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const {
    messages: rawMessages,
    addMessage,
    isLoading,
    sendMessage,
    initializeChat,
  } = useChatStore();
  // Ensure messages is always an array
  const messages = Array.isArray(rawMessages) ? rawMessages : [];
  const [summary, setSummary] = useState<string>("");

  useEffect(() => {
    initializeChat(user?.id || "anonymous");
  }, [user?.id, initializeChat]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    const fetchSummary = async () => {
      try {
        const res = await fetch("/api/chat/summary?session_id=default_session");
        if (res.ok) {
          const data = await res.json();
          setSummary(data.summary);
        }
      } catch (e) {
        // ignore
      }
    };
    fetchSummary();
  }, [messages.length]);

  const handleSendMessage = async (content: string) => {
    if (!content.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content,
      timestamp: new Date(),
    };

    addMessage(userMessage);
    await sendMessage(content, user?.id || "anonymous");
  };

  // Find the latest assistant message
  const latestAssistantMessageId = Array.isArray(messages)
    ? messages.filter((msg) => msg.role === "assistant").pop()?.id
    : undefined;

  return (
    <div className="flex flex-col h-full">
      {/* Context Summary */}
      {summary && (
        <div className="p-2 text-xs text-muted-foreground border-b bg-[#292A2D] dark:bg-[#292A2D] flex-shrink-0">
          {summary}
        </div>
      )}

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 min-h-0">
        {Array.isArray(messages) && messages.length === 0 && (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <h3 className="text-lg font-semibold mb-2">
                Welcome to JuristAI
              </h3>
              <p className="text-muted-foreground">
                Ask me anything about Nigerian law, legal documents, or legal
                procedures.
              </p>
            </div>
          </div>
        )}

        {Array.isArray(messages) &&
          messages.map((message) => (
            <ChatMessage
              key={message.id}
              message={message}
              isLatestAssistantMessage={message.id === latestAssistantMessageId}
            />
          ))}

        {isLoading && (
          <div className="flex items-center gap-2 text-muted-foreground">
            <LoadingSpinner size="sm" />
            <span>Consulting Nigerian law...</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Chat Input */}
      <div className="border-t p-4 flex-shrink-0">
        <ChatInput onSend={handleSendMessage} isLoading={isLoading} />
      </div>

      {/* Feedback Section */}
      {/* {Array.isArray(messages) && messages.length > 0 && messages[messages.length - 1].role === 'assistant' && (
        <div className="flex-shrink-0 mb-4">
          {Array.isArray(messages) && messages.length > 0 && (
            <FeedbackSection messageId={messages[messages.length - 1].id} />
          )}
        </div>
      )} */}
    </div>
  );
}
