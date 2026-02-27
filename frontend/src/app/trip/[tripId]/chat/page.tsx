"use client";

import { useEffect, useRef, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { Send, Compass, ArrowLeft } from "lucide-react";
import { cn } from "@/lib/utils";
import { useAuthStore } from "@/stores/auth-store";
import { useTripStore } from "@/stores/trip-store";
import { useConversationStore } from "@/stores/conversation-store";
import { BottomTabBar } from "@/components/layout/bottom-tab-bar";
import { api } from "@/lib/api";

interface CompanionMessage {
  role: "user" | "assistant";
  content: string;
}

export default function CompanionChatPage() {
  const params = useParams();
  const router = useRouter();
  const tripId = params.tripId as string;
  const { isAuthenticated } = useAuthStore();
  const { currentTrip } = useTripStore();
  const { conversationId, createConversation } = useConversationStore();

  const [messages, setMessages] = useState<CompanionMessage[]>([]);
  const [input, setInput] = useState("");
  const [isSending, setIsSending] = useState(false);
  const [convId, setConvId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!isAuthenticated) {
      router.push("/auth");
      return;
    }
  }, [isAuthenticated]);

  useEffect(() => {
    async function initChat() {
      if (!tripId || convId) return;

      try {
        const convs = await api.get<Array<{ id: string }>>(`/conversations?trip_id=${tripId}`);
        if (convs.length > 0) {
          setConvId(convs[0].id);
          const conv = await api.get<{ messages: Array<{ role: string; content: string }> }>(
            `/conversations/${convs[0].id}`
          );
          const companionMsgs = conv.messages
            .filter((m) => m.role !== "system")
            .map((m) => ({ role: m.role as "user" | "assistant", content: m.content }));
          setMessages(companionMsgs);
        } else {
          const conv = await api.post<{ id: string }>("/conversations", {
            trip_id: tripId,
            title: "Live Companion",
          });
          setConvId(conv.id);
          setMessages([
            {
              role: "assistant",
              content:
                "Hey! 👋 I'm right here with you on your trip. Ask me anything — today's conditions, activity tips, what to pack, or just chat about what you're seeing!",
            },
          ]);
        }
      } catch {
        setMessages([
          {
            role: "assistant",
            content: "Hey! I'm Buddi, your travel companion. How can I help you today?",
          },
        ]);
      }
    }
    initChat();
  }, [tripId]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || isSending || !convId) return;

    const userMessage = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: userMessage }]);
    setIsSending(true);

    try {
      const response = await api.post<{
        messages: Array<{ role: string; content: string }>;
      }>(`/conversations/${convId}/companion`, {
        content: userMessage,
      });

      const assistantMsg = response.messages.find((m) => m.role === "assistant");
      if (assistantMsg) {
        setMessages((prev) => [...prev, { role: "assistant", content: assistantMsg.content }]);
      }
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Sorry, I'm having trouble connecting right now. Try again in a moment!",
        },
      ]);
    }

    setIsSending(false);
  };

  return (
    <div className="min-h-screen bg-mist flex flex-col pb-20">
      {/* Header */}
      <div className="bg-forest text-white px-4 py-3 flex items-center gap-3 sticky top-0 z-40">
        <button onClick={() => router.push(`/trip/${tripId}/today`)} className="p-1">
          <ArrowLeft size={20} className="text-white" />
        </button>
        <div className="w-8 h-8 bg-white/20 rounded-full flex items-center justify-center">
          <Compass size={16} className="text-white" />
        </div>
        <div>
          <h1 className="text-sm font-semibold text-white">Chat with Buddi</h1>
          <p className="text-[10px] text-white/60">Your live companion</p>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-3">
        {messages.map((msg, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.03 }}
            className={cn("flex", msg.role === "user" ? "justify-end" : "justify-start")}
          >
            {msg.role === "assistant" && (
              <div className="w-7 h-7 bg-forest rounded-full flex items-center justify-center mr-2 mt-1 shrink-0">
                <Compass size={14} className="text-white" />
              </div>
            )}
            <div
              className={cn(
                "px-4 py-3 rounded-2xl text-sm leading-relaxed whitespace-pre-wrap",
                msg.role === "user"
                  ? "bg-teal text-white rounded-br-[4px] max-w-[75%]"
                  : "bg-sand text-bark rounded-bl-[4px] max-w-[85%]"
              )}
            >
              {msg.content}
            </div>
          </motion.div>
        ))}

        {isSending && (
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 bg-forest rounded-full flex items-center justify-center shrink-0">
              <Compass size={14} className="text-white" />
            </div>
            <div className="bg-sand rounded-2xl rounded-bl-[4px] px-4 py-3">
              <div className="flex gap-1">
                <span className="w-2 h-2 bg-stone/40 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                <span className="w-2 h-2 bg-stone/40 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                <span className="w-2 h-2 bg-stone/40 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="sticky bottom-20 left-0 right-0 bg-cloud border-t border-bark/10 px-4 py-3">
        <div className="flex items-center gap-2 max-w-lg mx-auto">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && sendMessage()}
            placeholder="Ask Buddi anything..."
            className="flex-1 bg-sand rounded-xl px-4 py-2.5 text-sm text-bark placeholder:text-driftwood focus:outline-none focus:ring-2 focus:ring-teal/30"
          />
          <button
            onClick={sendMessage}
            disabled={!input.trim() || isSending}
            className={cn(
              "w-10 h-10 rounded-xl flex items-center justify-center transition-colors",
              input.trim() ? "bg-teal text-white" : "bg-sand text-driftwood"
            )}
          >
            <Send size={18} />
          </button>
        </div>
      </div>

      <BottomTabBar tripId={tripId} />
    </div>
  );
}
