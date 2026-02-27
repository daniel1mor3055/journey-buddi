"use client";

import { create } from "zustand";
import { api } from "@/lib/api";

export interface ActivityReport {
  activity_id: string | null;
  activity_name: string;
  emoji: string;
  score: number;
  assessment: string;
  confidence: string;
  key_factors: Array<{ parameter: string; value: number; score: number; note: string }>;
  packing_suggestions: string[];
  timing_suggestion: string | null;
  pro_tips: string[];
  time_start: string | null;
  time_end: string | null;
}

export interface DailyBriefing {
  id: string;
  trip_id: string;
  day_number: number;
  briefing_date: string;
  location: string;
  overall_score: number;
  overall_assessment: string;
  confidence: string;
  weather_summary: {
    temp_min?: number;
    temp_max?: number;
    description?: string;
    icon?: string;
    avg_wind_kmh?: number;
    max_precip_prob?: number;
  };
  solar_data: {
    sunrise?: string;
    sunset?: string;
    day_length_hours?: number;
    golden_morning_start?: string;
    golden_evening_start?: string;
    moon_phase_name?: string;
    moon_illumination_pct?: number;
  };
  activity_reports: ActivityReport[];
  packing_list: string[];
  timeline: Array<{ time: string; activity: string }>;
  hidden_gem: string | null;
  lookahead: Array<{
    date: string;
    score: number;
    assessment: string;
    confidence: string;
    summary: string;
    temp_range: string;
  }>;
  ai_narrative: string | null;
  swap_suggestion: Record<string, unknown> | null;
  created_at: string;
}

export interface SwapSuggestion {
  id: string;
  trip_id: string;
  original_day: number;
  suggested_day: number;
  reason: string;
  improvement_score: number;
  disruption_score: number;
  recommendation: string;
  original_conditions: { score: number; assessment: string };
  suggested_conditions: { score: number; assessment: string };
  details: { original_location?: string; swap_location?: string };
  status: string;
  created_at: string;
}

export interface DayConditionReport {
  day_number: number;
  date: string | null;
  location: string;
  overall_score: number;
  overall_assessment: string;
  confidence: string;
  weather_summary: Record<string, unknown> | null;
  activity_reports: ActivityReport[];
}

interface CompanionState {
  briefings: DailyBriefing[];
  currentBriefing: DailyBriefing | null;
  conditions: DayConditionReport[];
  swaps: SwapSuggestion[];
  isLoading: boolean;
  error: string | null;

  fetchBriefings: (tripId: string) => Promise<void>;
  generateBriefings: (tripId: string, dayNumber?: number) => Promise<void>;
  fetchBriefing: (tripId: string, dayNumber: number) => Promise<void>;
  fetchConditions: (tripId: string) => Promise<void>;
  fetchSwaps: (tripId: string) => Promise<void>;
  handleSwap: (tripId: string, swapId: string, action: "accept" | "decline") => Promise<void>;
  activateTrip: (tripId: string) => Promise<void>;
  reset: () => void;
}

export const useCompanionStore = create<CompanionState>((set) => ({
  briefings: [],
  currentBriefing: null,
  conditions: [],
  swaps: [],
  isLoading: false,
  error: null,

  fetchBriefings: async (tripId) => {
    set({ isLoading: true });
    try {
      const briefings = await api.get<DailyBriefing[]>(`/trips/${tripId}/briefings`);
      set({ briefings, isLoading: false });
    } catch {
      set({ error: "Failed to load briefings", isLoading: false });
    }
  },

  generateBriefings: async (tripId, dayNumber) => {
    set({ isLoading: true });
    try {
      const body: Record<string, unknown> = {};
      if (dayNumber !== undefined) body.day_number = dayNumber;
      const briefings = await api.post<DailyBriefing[]>(`/trips/${tripId}/briefings/generate`, body);
      set({ briefings, isLoading: false });
    } catch {
      set({ error: "Failed to generate briefings", isLoading: false });
    }
  },

  fetchBriefing: async (tripId, dayNumber) => {
    try {
      const briefing = await api.get<DailyBriefing>(`/trips/${tripId}/briefings/${dayNumber}`);
      set({ currentBriefing: briefing });
    } catch {
      set({ currentBriefing: null });
    }
  },

  fetchConditions: async (tripId) => {
    try {
      const data = await api.get<{ days: DayConditionReport[] }>(`/conditions/forecast/${tripId}`);
      set({ conditions: data.days });
    } catch {
      set({ conditions: [] });
    }
  },

  fetchSwaps: async (tripId) => {
    try {
      const swaps = await api.get<SwapSuggestion[]>(`/trips/${tripId}/briefings/swaps/list`);
      set({ swaps });
    } catch {
      set({ swaps: [] });
    }
  },

  handleSwap: async (tripId, swapId, action) => {
    try {
      await api.post(`/trips/${tripId}/briefings/swaps/${swapId}/action`, { action });
      const swaps = await api.get<SwapSuggestion[]>(`/trips/${tripId}/briefings/swaps/list`);
      set({ swaps });
    } catch {
      set({ error: "Failed to process swap" });
    }
  },

  activateTrip: async (tripId) => {
    try {
      await api.post(`/conditions/trips/${tripId}/activate`);
    } catch {
      set({ error: "Failed to activate trip" });
    }
  },

  reset: () => set({ briefings: [], currentBriefing: null, conditions: [], swaps: [], isLoading: false, error: null }),
}));
