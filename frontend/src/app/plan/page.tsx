"use client";

import { useRouter } from "next/navigation";
import { useEffect, useRef, useState, useCallback, useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ArrowLeft, ChevronRight, Compass, Check, Send } from "lucide-react";
import Link from "next/link";
import { useConversationStore } from "@/stores/conversation-store";
import { useTripStore } from "@/stores/trip-store";
import { useAuthStore } from "@/stores/auth-store";
import type { ChoiceOption, ProviderCard, ChatMessage } from "@/stores/conversation-store";

function BuddiAvatar() {
  return (
    <div className="w-8 h-8 rounded-full bg-teal flex items-center justify-center shrink-0">
      <Compass className="text-white" size={16} />
    </div>
  );
}

function TypingIndicator() {
  return (
    <div className="flex items-center gap-2">
      <BuddiAvatar />
      <div className="bg-sand rounded-[18px] rounded-bl-[4px] px-4 py-3 flex gap-1">
        {[0, 1, 2].map((i) => (
          <motion.span
            key={i}
            className="w-2 h-2 rounded-full bg-driftwood"
            animate={{ opacity: [0.4, 1, 0.4] }}
            transition={{ duration: 0.8, repeat: Infinity, delay: i * 0.2 }}
          />
        ))}
      </div>
    </div>
  );
}

interface ChoiceCardsProps {
  choices: ChoiceOption[];
  multiSelect: boolean;
  selectedChoices: Set<string>;
  onToggle: (label: string) => void;
  onConfirm: () => void;
}

function ChoiceCards({
  choices,
  multiSelect,
  selectedChoices,
  onToggle,
  onConfirm,
}: ChoiceCardsProps) {
  const count = selectedChoices.size;
  return (
    <div className="space-y-3">
      <div className="grid grid-cols-2 gap-2 sm:grid-cols-3">
        {choices.map((opt) => {
          const selected = selectedChoices.has(opt.label);
          return (
            <button
              key={opt.label}
              type="button"
              onClick={() => onToggle(opt.label)}
              className={`
                relative flex flex-col items-start p-3 rounded-xl border-2 transition-all
                text-left hover:shadow-md
                ${selected ? "border-teal bg-teal/5" : "border-sand bg-cloud"}
              `}
            >
              <span className="text-xl mb-1">{opt.emoji}</span>
              <span className="text-bark font-medium" style={{ fontSize: "0.9375rem" }}>
                {opt.label}
              </span>
              {opt.desc && (
                <span className="text-stone mt-0.5" style={{ fontSize: "0.8125rem" }}>
                  {opt.desc}
                </span>
              )}
              {multiSelect && selected && (
                <div className="absolute top-2 right-2 w-5 h-5 rounded-full bg-teal flex items-center justify-center">
                  <Check className="text-white" size={12} />
                </div>
              )}
            </button>
          );
        })}
      </div>
      {multiSelect && count > 0 && (
        <button
          type="button"
          onClick={onConfirm}
          className="flex items-center gap-1 text-teal font-semibold"
          style={{ fontSize: "0.9375rem" }}
        >
          Continue with {count} selected
          <ChevronRight size={18} />
        </button>
      )}
    </div>
  );
}

interface ProviderCardsProps {
  cards: ProviderCard[];
  onSelect: (name: string) => void;
}

function ProviderCards({ cards, onSelect }: ProviderCardsProps) {
  return (
    <div className="space-y-3">
      {cards.map((card) => (
        <button
          key={card.name}
          type="button"
          onClick={() => onSelect(card.name)}
          className="w-full flex gap-3 p-4 rounded-xl border-2 border-sand bg-cloud hover:shadow-md transition-all text-left"
        >
          <span className="text-2xl shrink-0">{card.emoji}</span>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="text-bark font-semibold" style={{ fontSize: "0.9375rem" }}>
                {card.name}
              </span>
              {card.buddiPick && (
                <span className="px-2 py-0.5 rounded-md bg-teal/20 text-teal text-xs font-medium">
                  BuddiPick
                </span>
              )}
            </div>
            <p className="text-stone text-sm mt-0.5">{card.location}</p>
            <div className="flex items-center gap-3 mt-1 text-stone" style={{ fontSize: "0.8125rem" }}>
              <span>★ {card.rating}</span>
              <span>{card.reviews} reviews</span>
              <span>${card.price}</span>
            </div>
            <p className="text-driftwood mt-1" style={{ fontSize: "0.8125rem" }}>
              {card.whatsSpecial}
            </p>
          </div>
        </button>
      ))}
    </div>
  );
}

interface FreeTextInputProps {
  onSubmit: (text: string) => void;
  disabled: boolean;
}

function FreeTextInput({ onSubmit, disabled }: FreeTextInputProps) {
  const [value, setValue] = useState("");

  const handleSubmit = () => {
    const trimmed = value.trim();
    if (!trimmed || disabled) return;
    onSubmit(trimmed);
    setValue("");
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
    // Shift+Enter inserts a newline naturally via textarea default behaviour
  };

  return (
    <div className="flex gap-2 items-end">
      <textarea
        rows={1}
        value={value}
        onChange={(e) => {
          setValue(e.target.value);
          // Auto-grow: reset then set scrollHeight so it shrinks back too
          e.target.style.height = "auto";
          e.target.style.height = `${e.target.scrollHeight}px`;
        }}
        onKeyDown={handleKeyDown}
        placeholder="Type your answer… (Shift+Enter for new line)"
        disabled={disabled}
        className="flex-1 rounded-xl border-2 border-sand bg-cloud px-4 py-3 text-bark
          placeholder:text-stone focus:outline-none focus:border-teal transition-colors
          resize-none overflow-hidden leading-relaxed"
        style={{ fontSize: "0.9375rem", minHeight: "2.75rem", maxHeight: "10rem" }}
      />
      <button
        type="button"
        onClick={handleSubmit}
        disabled={disabled || !value.trim()}
        className="shrink-0 w-11 h-11 rounded-xl bg-teal text-white flex items-center justify-center
          disabled:opacity-40 transition-opacity hover:shadow-md active:scale-95"
      >
        <Send size={18} />
      </button>
    </div>
  );
}

export default function PlanPage() {
  const router = useRouter();
  const chatEndRef = useRef<HTMLDivElement>(null);
  const [selectedChoices, setSelectedChoices] = useState<Set<string>>(new Set());

  const { isAuthenticated, isLoading: authLoading, initialize } = useAuthStore();
  const { currentTrip, createTrip, fetchTrips } = useTripStore();
  const {
    conversationId,
    messages,
    planningStep,
    progressPercent,
    isLoading,
    createConversation,
    initConversation,
    sendMessage,
    goBack,
    reset: resetConversation,
  } = useConversationStore();

  const lastAssistantMsg = useMemo(
    () => [...messages].reverse().find((m) => m.role === "assistant") ?? null,
    [messages]
  );
  const lastAssistantMsgId = lastAssistantMsg?.id ?? null;

  const scrollToBottom = useCallback(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading, scrollToBottom]);

  // Clear multi-select state whenever messages advance so stale selections
  // from a previous step don't carry over to the next question.
  useEffect(() => {
    setSelectedChoices(new Set());
  }, [lastAssistantMsgId]);

  useEffect(() => {
    initialize();
  }, [initialize]);

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.replace("/auth");
    }
  }, [authLoading, isAuthenticated, router]);

  useEffect(() => {
    if (authLoading || !isAuthenticated) return;

    let mounted = true;

    async function setup() {
      let tripId: string;

      if (!currentTrip) {
        await fetchTrips();
        const trip = await createTrip("New Zealand");
        if (!mounted) return;
        tripId = trip.id;
      } else {
        tripId = currentTrip.id;
      }

      resetConversation();
      await createConversation(tripId);
      if (!mounted) return;
      await initConversation();
    }

    setup();
    return () => {
      mounted = false;
    };
  }, [authLoading, isAuthenticated]); // eslint-disable-line react-hooks/exhaustive-deps

  const handleChoiceToggle = useCallback((label: string) => {
    setSelectedChoices((prev) => {
      const next = new Set(prev);
      if (next.has(label)) next.delete(label);
      else next.add(label);
      return next;
    });
  }, []);

  const handleMultiSelectConfirm = useCallback(() => {
    if (selectedChoices.size === 0) return;
    const content = Array.from(selectedChoices).join(", ");
    sendMessage(content);
    setSelectedChoices(new Set());
  }, [selectedChoices, sendMessage]);

  const handleSingleChoice = useCallback(
    (label: string) => {
      sendMessage(label);
    },
    [sendMessage]
  );

  const handleProviderSelect = useCallback(
    (name: string) => {
      sendMessage(name);
    },
    [sendMessage]
  );

  if (authLoading || !isAuthenticated) {
    return (
      <div className="min-h-screen bg-mist flex items-center justify-center">
        <div className="text-stone">Loading...</div>
      </div>
    );
  }

  const showViewDashboard = planningStep === "complete";
  const tripId = currentTrip?.id;

  const showFreeText = !isLoading && lastAssistantMsg?.metadata_?.free_text === true;

  return (
    <div className="min-h-screen bg-mist flex flex-col">
      {/* Sticky header */}
      <header className="sticky top-0 z-40 bg-forest text-white px-4 py-3 flex items-center gap-3">
        <Link
          href="/dashboard"
          className="p-2 -ml-2 rounded-lg hover:bg-white/10 transition-colors"
          aria-label="Back to dashboard"
        >
          <ArrowLeft size={20} />
        </Link>
        <h1 className="font-bold flex-1 text-white" style={{ fontSize: "0.9375rem" }}>
          Planning Your NZ Trip
        </h1>
      </header>

      {/* Progress bar */}
      <div className="h-1.5 bg-sand">
        <motion.div
          className="h-full bg-teal"
          initial={{ width: 0 }}
          animate={{ width: `${progressPercent}%` }}
          transition={{ duration: 0.4 }}
        />
      </div>

      {/* Chat area */}
      <main className="flex-1 overflow-y-auto px-4 py-6 max-w-2xl mx-auto w-full">
        <div className="space-y-4">
          <AnimatePresence mode="popLayout">
            {messages.map((msg) => (
              <MessageBubble
                key={msg.id}
                message={msg}
                isActive={!isLoading && msg.id === lastAssistantMsgId}
                onSingleChoice={handleSingleChoice}
                onChoiceToggle={handleChoiceToggle}
                onMultiSelectConfirm={handleMultiSelectConfirm}
                onProviderSelect={handleProviderSelect}
                selectedChoices={selectedChoices}
              />
            ))}
          </AnimatePresence>

          {isLoading && <TypingIndicator />}

          {showFreeText && (
            <div className="pt-2">
              <FreeTextInput onSubmit={(text) => sendMessage(text)} disabled={isLoading} />
            </div>
          )}

          <div ref={chatEndRef} />
        </div>

        {/* Action buttons when step is GENERATING or CONFIRMED */}
        {showViewDashboard && tripId && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-8 space-y-3"
          >
            <Link
              href={`/trip/${tripId}`}
              className="block w-full bg-teal text-white rounded-xl py-3 px-6 font-semibold text-center transition-all hover:shadow-md active:scale-[0.98]"
            >
              View Full Dashboard
            </Link>
            <button
              type="button"
              onClick={() => goBack()}
              className="block w-full bg-sand text-bark rounded-xl py-3 px-6 font-semibold transition-all hover:shadow-md active:scale-[0.98]"
            >
              I Want to Make Changes
            </button>
          </motion.div>
        )}
      </main>
    </div>
  );
}

interface MessageBubbleProps {
  message: ChatMessage;
  isActive: boolean;
  onSingleChoice: (label: string) => void;
  onChoiceToggle: (label: string) => void;
  onMultiSelectConfirm: () => void;
  onProviderSelect: (name: string) => void;
  selectedChoices: Set<string>;
}

function MessageBubble({
  message,
  isActive,
  onSingleChoice,
  onChoiceToggle,
  onMultiSelectConfirm,
  onProviderSelect,
  selectedChoices,
}: MessageBubbleProps) {
  const choices = message.metadata_?.choices ?? [];
  const multiSelect = message.metadata_?.multi_select ?? false;
  const providerCards = message.metadata_?.provider_cards ?? [];

  const isUser = message.role === "user";

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0 }}
      className={isUser ? "flex justify-end" : "flex justify-start"}
    >
      <div className={`flex gap-2 max-w-[85%] sm:max-w-[75%] ${isUser ? "flex-row-reverse" : ""}`}>
        {!isUser && <BuddiAvatar />}
        <div className={`flex flex-col gap-2 ${isUser ? "items-end" : "items-start"}`}>
          {message.content && (
            <div
              className={
                isUser
                  ? "bg-teal text-white rounded-[18px] rounded-br-[4px] px-4 py-3"
                  : "bg-sand text-bark rounded-[18px] rounded-bl-[4px] px-4 py-3 whitespace-pre-wrap"
              }
              style={{ fontSize: "0.9375rem" }}
            >
              {message.content}
            </div>
          )}
          {choices.length > 0 && isActive && (
            <ChoiceCards
              choices={choices}
              multiSelect={multiSelect}
              selectedChoices={selectedChoices}
              onToggle={multiSelect ? onChoiceToggle : (l) => onSingleChoice(l)}
              onConfirm={onMultiSelectConfirm}
            />
          )}
          {providerCards.length > 0 && isActive && (
            <ProviderCards cards={providerCards} onSelect={onProviderSelect} />
          )}
        </div>
        {isUser && <div className="w-8 shrink-0" />}
      </div>
    </motion.div>
  );
}
