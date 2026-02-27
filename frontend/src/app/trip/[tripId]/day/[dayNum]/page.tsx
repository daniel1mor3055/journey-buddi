"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { ArrowLeft, ChevronDown, ChevronUp, Compass, LogOut } from "lucide-react";
import {
  useTripStore,
  type ItineraryDay,
  type ItineraryActivity,
} from "@/stores/trip-store";
import { useAuthStore } from "@/stores/auth-store";
import { cn } from "@/lib/utils";

interface ActivityCardProps {
  activity: ItineraryActivity;
  isExpanded: boolean;
  onToggle: () => void;
}

function ActivityCard({ activity, isExpanded, onToggle }: ActivityCardProps) {
  const timeRange =
    activity.time_start && activity.time_end
      ? `${activity.time_start} – ${activity.time_end}`
      : activity.time_start ?? "—";

  return (
    <motion.div
      layout
      className="bg-cloud rounded-2xl p-4 shadow-sm overflow-hidden"
    >
      <div
        className="flex items-start justify-between gap-2 cursor-pointer"
        onClick={onToggle}
      >
        <div className="flex-1 min-w-0">
          <span className="text-lg mr-1">{activity.emoji}</span>
          <span className="text-bark font-semibold">{activity.name}</span>
        </div>
        <button
          className="p-1 rounded-lg hover:bg-sand transition-colors shrink-0"
          aria-label={isExpanded ? "Collapse" : "Expand"}
        >
          {isExpanded ? (
            <ChevronUp size={18} className="text-stone" />
          ) : (
            <ChevronDown size={18} className="text-stone" />
          )}
        </button>
      </div>

      <div className="mt-2 text-stone text-sm flex flex-wrap gap-x-4 gap-y-1">
        {activity.provider && <span>{activity.provider}</span>}
        <span>{timeRange}</span>
        {activity.price > 0 && (
          <span>
            {activity.currency} {activity.price}
          </span>
        )}
      </div>

      {activity.booking_status && (
        <span
          className={cn(
            "inline-block mt-2 text-xs px-2 py-0.5 rounded-full",
            activity.booking_status === "confirmed"
              ? "bg-green-100 text-green-800"
              : activity.booking_status === "pending"
                ? "bg-amber-100 text-amber-800"
                : "bg-sand text-bark"
          )}
        >
          {activity.booking_status}
        </span>
      )}

      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="mt-3 pt-3 border-t border-sand"
          >
            {activity.booking_ref && (
              <p className="text-stone text-sm">Ref: {activity.booking_ref}</p>
            )}
            {activity.condition_score != null && (
              <p className="text-stone text-sm mt-1">
                Condition score: {(activity.condition_score * 100).toFixed(0)}%
              </p>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

export default function DayDetailPage() {
  const params = useParams();
  const router = useRouter();
  const tripId = params.tripId as string;
  const dayNum = parseInt(params.dayNum as string, 10);

  const { trips, itinerary, fetchTrips, fetchItinerary } = useTripStore();
  const { user, isAuthenticated, isLoading: authLoading, initialize, logout } =
    useAuthStore();

  const [expandedActivityIds, setExpandedActivityIds] = useState<Set<string>>(
    new Set()
  );

  const trip = trips.find((t) => t.id === tripId);
  const day: ItineraryDay | undefined = itinerary?.days.find(
    (d) => d.day_number === dayNum
  );

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
    }
  }, [tripId, fetchTrips, fetchItinerary]);

  const toggleActivity = (id: string) => {
    setExpandedActivityIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const accommodation = day?.accommodation as
    | {
        name?: string;
        address?: string;
        check_in?: string;
        check_out?: string;
        booking_status?: string;
        price_per_night?: number;
      }
    | undefined;

  const transport = day?.transport as
    | {
        origin?: string;
        destination?: string;
        distance?: string;
        duration?: string;
      }
    | undefined;

  const totalDays = itinerary?.total_days ?? 0;
  const prevDay = dayNum > 1 ? dayNum - 1 : null;
  const nextDay = dayNum < totalDays ? dayNum + 1 : null;

  if (authLoading) {
    return (
      <div className="min-h-screen bg-mist flex items-center justify-center">
        <div className="text-stone">Loading...</div>
      </div>
    );
  }

  if (!isAuthenticated || !user) return null;

  if (!day && itinerary) {
    return (
      <div className="min-h-screen bg-mist flex items-center justify-center">
        <div className="text-stone">Day {dayNum} not found</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-mist pb-8">
      <header className="bg-forest text-white px-4 py-3 flex items-center justify-between sticky top-0 z-40">
        <div className="flex items-center gap-2">
          <button
            onClick={() => router.push(`/trip/${tripId}`)}
            className="p-2 -ml-2 rounded-lg hover:bg-white/10 transition-colors"
            aria-label="Back"
          >
            <ArrowLeft size={20} />
          </button>
          <div className="w-8 h-8 rounded-full bg-teal flex items-center justify-center">
            <Compass className="text-white" size={18} />
          </div>
          <span className="font-bold text-lg truncate max-w-[200px]">
            Day {dayNum} — {day?.location ?? "…"}
          </span>
        </div>
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
      </header>

      <main className="max-w-2xl mx-auto px-4 py-6 space-y-6">
        {day && (
          <>
            <motion.div
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-cloud rounded-2xl p-4 shadow-sm"
            >
              <h3 className="text-bark font-semibold">Location</h3>
              <p className="text-stone mt-1">{day.location}</p>
            </motion.div>

            {transport && (transport.origin || transport.destination) && (
              <motion.div
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.05 }}
                className="bg-cloud rounded-2xl p-4 shadow-sm"
              >
                <h3 className="text-bark font-semibold">Transport</h3>
                <div className="mt-2 text-stone text-sm space-y-1">
                  {transport.origin && (
                    <p>From: {transport.origin}</p>
                  )}
                  {transport.destination && (
                    <p>To: {transport.destination}</p>
                  )}
                  {(transport.distance || transport.duration) && (
                    <p>
                      {transport.duration ?? ""}
                      {transport.duration && transport.distance ? " · " : ""}
                      {transport.distance ?? ""}
                    </p>
                  )}
                </div>
              </motion.div>
            )}

            <motion.div
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="bg-cloud rounded-2xl p-4 shadow-sm"
            >
              <h3 className="text-bark font-semibold mb-3">Timeline</h3>
              <div className="space-y-2">
                {day.activities
                  .sort((a, b) => a.sort_order - b.sort_order)
                  .map((a) => (
                    <div
                      key={a.id}
                      className="flex items-center gap-2 text-stone text-sm"
                    >
                      <span className="text-bark font-medium w-24 shrink-0">
                        {a.time_start ?? "—"}
                      </span>
                      <span>{a.emoji} {a.name}</span>
                    </div>
                  ))}
              </div>
            </motion.div>

            <div className="space-y-4">
              <h3 className="text-bark font-semibold">Activities</h3>
              {day.activities.map((activity) => (
                <ActivityCard
                  key={activity.id}
                  activity={activity}
                  isExpanded={expandedActivityIds.has(activity.id)}
                  onToggle={() => toggleActivity(activity.id)}
                />
              ))}
            </div>

            {accommodation?.name && (
              <motion.div
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-cloud rounded-2xl p-4 shadow-sm"
              >
                <h3 className="text-bark font-semibold">Accommodation</h3>
                <p className="text-bark mt-1 font-medium">🏨 {accommodation.name}</p>
                {accommodation.address && (
                  <p className="text-stone text-sm mt-1">{accommodation.address}</p>
                )}
                {(accommodation.check_in || accommodation.check_out) && (
                  <p className="text-stone text-sm mt-1">
                    Check-in: {accommodation.check_in ?? "—"} · Check-out:{" "}
                    {accommodation.check_out ?? "—"}
                  </p>
                )}
                {accommodation.booking_status && (
                  <span
                    className={cn(
                      "inline-block mt-2 text-xs px-2 py-0.5 rounded-full",
                      accommodation.booking_status === "confirmed"
                        ? "bg-green-100 text-green-800"
                        : "bg-sand text-bark"
                    )}
                  >
                    {accommodation.booking_status}
                  </span>
                )}
                {accommodation.price_per_night != null &&
                  accommodation.price_per_night > 0 && (
                    <p className="text-stone text-sm mt-2">
                      {accommodation.price_per_night} / night
                    </p>
                  )}
              </motion.div>
            )}

            <div className="flex items-center justify-between gap-4 pt-4">
              <button
                onClick={() =>
                  prevDay && router.push(`/trip/${tripId}/day/${prevDay}`)
                }
                disabled={!prevDay}
                className={cn(
                  "flex-1 py-3 rounded-xl font-semibold transition-all",
                  prevDay
                    ? "bg-sand text-bark hover:bg-sand/80"
                    : "bg-sand/50 text-stone cursor-not-allowed"
                )}
              >
                ← Previous
              </button>
              <button
                onClick={() =>
                  nextDay && router.push(`/trip/${tripId}/day/${nextDay}`)
                }
                disabled={!nextDay}
                className={cn(
                  "flex-1 py-3 rounded-xl font-semibold transition-all",
                  nextDay
                    ? "bg-teal text-white hover:shadow-md"
                    : "bg-teal/50 text-white/70 cursor-not-allowed"
                )}
              >
                Next →
              </button>
            </div>
          </>
        )}
      </main>
    </div>
  );
}
