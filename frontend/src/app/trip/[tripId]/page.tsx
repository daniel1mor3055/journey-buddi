"use client";

import { useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import {
  Map as MapIcon,
  Plus,
  ArrowLeft,
  Compass,
  LogOut,
} from "lucide-react";
import { useTripStore, type ItineraryDay } from "@/stores/trip-store";
import { useAuthStore } from "@/stores/auth-store";
import { useCompanionStore } from "@/stores/companion-store";
import { BottomTabBar } from "@/components/layout/bottom-tab-bar";
import { cn } from "@/lib/utils";

interface DayCardProps {
  day: ItineraryDay;
  tripId: string;
}

const CONDITION_DOT: Record<string, string> = {
  EXCELLENT: "bg-excellent",
  GOOD: "bg-good",
  FAIR: "bg-fair",
  POOR: "bg-poor",
  UNSAFE: "bg-unsafe",
};

function DayCard({ day, tripId, conditionReport }: DayCardProps & { conditionReport?: { overall_score: number; overall_assessment: string } }) {
  const router = useRouter();
  const score = conditionReport?.overall_score ?? day.activities[0]?.condition_score ?? null;
  const assessment = conditionReport?.overall_assessment ?? "GOOD";
  const dotColor = CONDITION_DOT[assessment] || "bg-good";

  const accommodation = day.accommodation as { name?: string } | undefined;
  const transport = day.transport as {
    origin?: string;
    destination?: string;
    duration?: string;
  } | undefined;

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.3 }}
      onClick={() => router.push(`/trip/${tripId}/day/${day.day_number}`)}
      className="bg-cloud rounded-2xl p-4 shadow-sm cursor-pointer active:scale-[0.99] transition-transform"
    >
      <div className="flex items-start justify-between gap-2">
        <div>
          <span className="text-bark font-semibold">Day {day.day_number}</span>
          <span className="text-stone text-sm ml-2">{day.location}</span>
        </div>
        <div className="flex items-center gap-1.5">
          {score !== null && (
            <span className="text-[10px] font-mono text-stone">{score}</span>
          )}
          <div className={cn("w-2.5 h-2.5 rounded-full shrink-0", dotColor)} />
        </div>
      </div>

      {day.activities.length > 0 && (
        <div className="mt-2 flex flex-wrap gap-1.5">
          {day.activities.slice(0, 4).map((a) => (
            <span
              key={a.id}
              className="text-stone text-sm"
            >{`${a.emoji} ${a.name.length > 12 ? a.name.slice(0, 12) + "…" : a.name}`}</span>
          ))}
          {day.activities.length > 4 && (
            <span className="text-stone text-sm">+{day.activities.length - 4}</span>
          )}
        </div>
      )}

      {accommodation?.name && (
        <div className="mt-2 text-stone text-sm">🏨 {accommodation.name}</div>
      )}

      {transport?.origin && (
        <div className="mt-1 text-stone text-sm">
          🚗 {transport.duration ?? "—"} · {transport.origin}
        </div>
      )}

      {day.is_flex_day && (
        <span className="inline-block mt-2 text-xs bg-sand text-bark px-2 py-0.5 rounded-full">
          Flex day
        </span>
      )}
      {day.is_arrival && (
        <span className="inline-block mt-2 ml-1 text-xs bg-teal/20 text-teal px-2 py-0.5 rounded-full">
          Arrival
        </span>
      )}
    </motion.div>
  );
}

export default function TripItineraryPage() {
  const params = useParams();
  const router = useRouter();
  const tripId = params.tripId as string;

  const {
    trips,
    itinerary,
    isLoading,
    fetchTrips,
    fetchItinerary,
    generateItinerary,
  } = useTripStore();
  const { user, isAuthenticated, isLoading: authLoading, initialize, logout } =
    useAuthStore();
  const { conditions, fetchConditions } = useCompanionStore();

  const trip = trips.find((t) => t.id === tripId);

  useEffect(() => {
    initialize();
  }, [initialize]);

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.replace("/auth");
    }
  }, [authLoading, isAuthenticated, router]);

  useEffect(() => {
    if (tripId) {
      fetchTrips();
      fetchItinerary(tripId);
      fetchConditions(tripId);
    }
  }, [tripId, fetchTrips, fetchItinerary, fetchConditions]);

  const isGenerating = isLoading && !itinerary;
  const hasItinerary = itinerary && itinerary.days.length > 0;

  if (authLoading) {
    return (
      <div className="min-h-screen bg-mist flex items-center justify-center">
        <div className="text-stone">Loading...</div>
      </div>
    );
  }

  if (!isAuthenticated || !user) return null;

  return (
    <div className="min-h-screen bg-mist pb-24">
      <header className="bg-forest text-white px-4 py-3 flex items-center justify-between sticky top-0 z-40">
        <div className="flex items-center gap-2">
          <button
            onClick={() => router.back()}
            className="p-2 -ml-2 rounded-lg hover:bg-white/10 transition-colors"
            aria-label="Back"
          >
            <ArrowLeft size={20} />
          </button>
          <div className="w-8 h-8 rounded-full bg-teal flex items-center justify-center">
            <Compass className="text-white" size={18} />
          </div>
          <span className="font-bold text-lg truncate max-w-[180px]">
            {trip?.destination ?? "Trip"}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => router.push(`/trip/${tripId}/map`)}
            className="p-2 rounded-lg hover:bg-white/10 transition-colors"
            aria-label="Map"
          >
            <MapIcon size={20} />
          </button>
          <button
            onClick={() => {
              logout();
              router.replace("/");
            }}
            className="p-2 rounded-lg hover:bg-white/10 transition-colors"
            aria-label="Log out"
          >
            <LogOut size={18} />
          </button>
        </div>
      </header>

      <main className="max-w-2xl mx-auto px-4 py-6">
        {isGenerating && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="bg-cloud rounded-2xl p-8 text-center"
          >
            <div className="animate-pulse text-stone">Generating itinerary…</div>
            <button
              onClick={() => generateItinerary(tripId)}
              disabled
              className="mt-4 bg-teal/60 text-white rounded-xl py-2 px-4 text-sm"
            >
              Generating…
            </button>
          </motion.div>
        )}

        {!hasItinerary && !isGenerating && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-cloud rounded-2xl p-8 text-center shadow-sm"
          >
            <h3 className="text-bark mb-2 text-lg font-semibold">
              No itinerary yet
            </h3>
            <p className="text-stone mb-6 text-sm">
              Generate an itinerary to see your trip days and activities.
            </p>
            <button
              onClick={() => generateItinerary(tripId)}
              disabled={isLoading}
              className="bg-teal text-white rounded-xl py-3 px-8 font-semibold transition-all hover:shadow-md active:scale-[0.98] inline-flex items-center gap-2 disabled:opacity-60"
            >
              <Plus size={20} />
              Generate Itinerary
            </button>
          </motion.div>
        )}

        {hasItinerary && itinerary && (
          <>
            <div className="bg-sand rounded-2xl p-4 mb-6">
              <div className="text-bark font-semibold">
                {itinerary.total_days} days · {itinerary.total_activities} activities
              </div>
              <div className="text-stone text-sm mt-1">
                {itinerary.booked_count} booked · {itinerary.needs_booking_count} need
                booking
              </div>
            </div>

            <div className="space-y-4">
              <AnimatePresence mode="popLayout">
                {itinerary.days.map((day) => {
                  const dayCondition = conditions.find(c => c.day_number === day.day_number);
                  return (
                    <DayCard
                      key={day.id}
                      day={day}
                      tripId={tripId}
                      conditionReport={dayCondition ? { overall_score: dayCondition.overall_score, overall_assessment: dayCondition.overall_assessment } : undefined}
                    />
                  );
                })}
              </AnimatePresence>
            </div>
          </>
        )}
      </main>

      <BottomTabBar tripId={tripId} />
    </div>
  );
}
