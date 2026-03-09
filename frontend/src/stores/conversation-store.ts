"use client";

import { create } from "zustand";
import { api } from "@/lib/api";

export interface ChoiceOption {
  emoji: string;
  label: string;
  desc?: string;
}

export interface ProviderCard {
  emoji: string;
  name: string;
  location: string;
  rating: number;
  reviews: number;
  price: number;
  whatsSpecial: string;
  buddiPick?: boolean;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  message_type: string;
  metadata_: {
    choices?: ChoiceOption[];
    multi_select?: boolean;
    free_text?: boolean;
    provider_cards?: ProviderCard[];
  };
  sort_order: number;
  created_at: string;
}

interface PlanningStepResponse {
  messages: ChatMessage[];
  planning_step: string;
  planning_state: Record<string, unknown>;
  progress_percent: number;
}

interface ConversationState {
  conversationId: string | null;
  messages: ChatMessage[];
  planningStep: string;
  planningState: Record<string, unknown>;
  progressPercent: number;
  isLoading: boolean;
  error: string | null;

  createConversation: (tripId: string) => Promise<void>;
  initConversation: () => Promise<void>;
  sendMessage: (content: string, messageType?: string) => Promise<void>;
  goBack: () => Promise<void>;
  reset: () => void;
}

export const useConversationStore = create<ConversationState>((set, get) => ({
  conversationId: null,
  messages: [],
  planningStep: "greeting",
  planningState: {},
  progressPercent: 0,
  isLoading: false,
  error: null,

  createConversation: async (tripId: string) => {
    set({ isLoading: true, error: null });
    try {
      const conv = await api.post<{ id: string; planning_step: string }>("/conversations", {
        trip_id: tripId,
      });
      set({
        conversationId: conv.id,
        planningStep: conv.planning_step,
        isLoading: false,
      });
    } catch (err) {
      set({ error: "Failed to start conversation", isLoading: false });
    }
  },

  initConversation: async () => {
    const { conversationId } = get();
    if (!conversationId) return;
    set({ isLoading: true });
    try {
      const data = await api.post<PlanningStepResponse>(
        `/conversations/${conversationId}/init`
      );
      set({
        messages: data.messages,
        planningStep: data.planning_step,
        planningState: data.planning_state,
        progressPercent: data.progress_percent,
        isLoading: false,
      });
    } catch (err) {
      set({ error: "Failed to initialize conversation", isLoading: false });
    }
  },

  sendMessage: async (content: string, messageType = "text") => {
    const { conversationId } = get();
    if (!conversationId) return;

    const optimisticId = `optimistic-${Date.now()}`;
    const optimisticMessage: ChatMessage = {
      id: optimisticId,
      role: "user",
      content,
      message_type: messageType,
      metadata_: {},
      sort_order: get().messages.length,
      created_at: new Date().toISOString(),
    };

    set((state) => ({
      messages: [...state.messages, optimisticMessage],
      isLoading: true,
      error: null,
    }));

    try {
      const data = await api.post<PlanningStepResponse>(
        `/conversations/${conversationId}/messages`,
        { content, message_type: messageType }
      );
      set((state) => ({
        messages: [
          ...state.messages.filter((m) => m.id !== optimisticId),
          ...data.messages,
        ],
        planningStep: data.planning_step,
        planningState: data.planning_state,
        progressPercent: data.progress_percent,
        isLoading: false,
      }));
    } catch (err) {
      set((state) => ({
        messages: state.messages.filter((m) => m.id !== optimisticId),
        error: "Failed to send message",
        isLoading: false,
      }));
    }
  },

  goBack: async () => {
    const { conversationId } = get();
    if (!conversationId) return;
    set({ isLoading: true });
    try {
      const data = await api.post<PlanningStepResponse>(
        `/conversations/${conversationId}/back`
      );
      set({
        messages: data.messages,
        planningStep: data.planning_step,
        planningState: data.planning_state,
        progressPercent: data.progress_percent,
        isLoading: false,
      });
    } catch (err) {
      set({ error: "Failed to go back", isLoading: false });
    }
  },

  reset: () => {
    set({
      conversationId: null,
      messages: [],
      planningStep: "greeting",
      planningState: {},
      progressPercent: 0,
      isLoading: false,
      error: null,
    });
  },
}));
