"use client";

import { create } from "zustand";
import { api } from "@/lib/api";

export interface ItineraryActivity {
  id: string;
  name: string;
  emoji: string;
  provider: string | null;
  time_start: string | null;
  time_end: string | null;
  price: number;
  currency: string;
  booking_status: string;
  booking_ref: string | null;
  condition_score: number | null;
  sort_order: number;
}

export interface ItineraryDay {
  id: string;
  trip_id: string;
  day_number: number;
  date: string | null;
  location: string;
  title: string | null;
  summary: string | null;
  is_flex_day: boolean;
  is_arrival: boolean;
  is_departure: boolean;
  is_locked: boolean;
  accommodation: Record<string, unknown>;
  transport: Record<string, unknown>;
  weather: Record<string, unknown>;
  activities: ItineraryActivity[];
}

export interface Trip {
  id: string;
  destination: string;
  destination_region: string | null;
  status: string;
  start_date: string | null;
  end_date: string | null;
  planning_state: Record<string, unknown>;
  created_at: string;
}

export interface ItineraryOverview {
  trip_id: string;
  total_days: number;
  total_activities: number;
  booked_count: number;
  needs_booking_count: number;
  flex_days: number;
  days: ItineraryDay[];
}

interface TripState {
  trips: Trip[];
  currentTrip: Trip | null;
  itinerary: ItineraryOverview | null;
  isLoading: boolean;
  error: string | null;

  fetchTrips: () => Promise<void>;
  createTrip: (destination: string) => Promise<Trip>;
  setCurrentTrip: (trip: Trip) => void;
  fetchItinerary: (tripId: string) => Promise<void>;
  generateItinerary: (tripId: string) => Promise<void>;
}

export const useTripStore = create<TripState>((set) => ({
  trips: [],
  currentTrip: null,
  itinerary: null,
  isLoading: false,
  error: null,

  fetchTrips: async () => {
    set({ isLoading: true });
    try {
      const trips = await api.get<Trip[]>("/trips");
      set({ trips, isLoading: false });
    } catch {
      set({ error: "Failed to load trips", isLoading: false });
    }
  },

  createTrip: async (destination: string) => {
    const trip = await api.post<Trip>("/trips", { destination });
    set((state) => ({
      trips: [trip, ...state.trips],
      currentTrip: trip,
    }));
    return trip;
  },

  setCurrentTrip: (trip: Trip) => {
    set({ currentTrip: trip });
  },

  fetchItinerary: async (tripId: string) => {
    set({ isLoading: true });
    try {
      const itinerary = await api.get<ItineraryOverview>(
        `/trips/${tripId}/itinerary`
      );
      set({ itinerary, isLoading: false });
    } catch {
      set({ itinerary: null, isLoading: false });
    }
  },

  generateItinerary: async (tripId: string) => {
    set({ isLoading: true });
    try {
      const itinerary = await api.post<ItineraryOverview>(
        `/trips/${tripId}/itinerary/generate`
      );
      set({ itinerary, isLoading: false });
    } catch (err) {
      set({ error: "Failed to generate itinerary", isLoading: false });
    }
  },
}));
