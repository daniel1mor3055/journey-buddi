"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { motion } from "framer-motion";
import {
  Cloud, Wind, Thermometer, Sunrise, Sunset,
  ChevronDown, ChevronUp, Compass, Sparkles, Eye,
  CheckCircle2, AlertTriangle,
} from "lucide-react";
import { useCompanionStore, DailyBriefing, ActivityReport } from "@/stores/companion-store";
import { useTripStore } from "@/stores/trip-store";
import { useAuthStore } from "@/stores/auth-store";
import { BottomTabBar } from "@/components/layout/bottom-tab-bar";
import { ConditionBadge, ConditionAssessment } from "@/components/ui/condition-badge";

export default function TodayPage() {
  const params = useParams();
  const router = useRouter();
  const tripId = params.tripId as string;
  const { isAuthenticated } = useAuthStore();
  const { currentTrip, fetchItinerary, itinerary } = useTripStore();
  const { briefings, generateBriefings, isLoading, swaps, fetchSwaps } = useCompanionStore();

  const [currentBriefing, setCurrentBriefing] = useState<DailyBriefing | null>(null);
  const [expandedActivity, setExpandedActivity] = useState<string | null>(null);

  useEffect(() => {
    if (!isAuthenticated) {
      router.push("/auth");
      return;
    }
    if (tripId) {
      fetchItinerary(tripId);
      generateBriefings(tripId);
      fetchSwaps(tripId);
    }
  }, [tripId, isAuthenticated]);

  useEffect(() => {
    if (briefings.length > 0) {
      const todayNum = _getCurrentDayNumber(currentTrip);
      const todayBriefing = briefings.find(b => b.day_number === todayNum) || briefings[0];
      setCurrentBriefing(todayBriefing);
    }
  }, [briefings, currentTrip]);

  if (isLoading && !currentBriefing) {
    return (
      <div className="min-h-screen bg-mist flex items-center justify-center">
        <div className="text-center">
          <Compass className="w-8 h-8 text-teal animate-spin mx-auto mb-3" />
          <p className="text-stone">Preparing your daily briefing...</p>
        </div>
      </div>
    );
  }

  if (!currentBriefing) {
    return (
      <div className="min-h-screen bg-mist pb-24">
        <div className="bg-forest text-white px-4 py-6">
          <h1 className="text-xl font-bold text-white">Today</h1>
          <p className="text-white/70 text-sm mt-1">No briefing available yet</p>
        </div>
        <div className="px-4 py-8 text-center">
          <Compass className="w-12 h-12 text-driftwood mx-auto mb-4" />
          <p className="text-stone mb-4">Generate briefings to see today&apos;s conditions and plan.</p>
          <button
            onClick={() => generateBriefings(tripId)}
            className="bg-teal text-white px-6 py-3 rounded-xl font-semibold"
          >
            Generate Briefings
          </button>
        </div>
        <BottomTabBar tripId={tripId} />
      </div>
    );
  }

  const ws = currentBriefing.weather_summary;
  const solar = currentBriefing.solar_data;

  return (
    <div className="min-h-screen bg-mist pb-24">
      {/* Header */}
      <div className="bg-forest text-white px-4 pt-4 pb-5">
        <p className="text-white/60 text-xs font-medium">
          Day {currentBriefing.day_number} · {currentBriefing.briefing_date}
        </p>
        <h1 className="text-xl font-bold text-white mt-1">
          📍 {currentBriefing.location}
        </h1>
        {ws?.temp_min != null && (
          <div className="flex items-center gap-4 mt-3 text-white/80 text-sm">
            <span className="flex items-center gap-1">
              <Thermometer size={14} />
              {ws.temp_min}–{ws.temp_max}°C
            </span>
            {ws.description && (
              <span className="flex items-center gap-1">
                <Cloud size={14} />
                {ws.description}
              </span>
            )}
            {ws.avg_wind_kmh != null && (
              <span className="flex items-center gap-1">
                <Wind size={14} />
                {ws.avg_wind_kmh} km/h
              </span>
            )}
          </div>
        )}
        {solar?.sunrise && (
          <div className="flex items-center gap-4 mt-2 text-white/60 text-xs">
            <span className="flex items-center gap-1">
              <Sunrise size={12} /> {new Date(solar.sunrise).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
            </span>
            {solar.sunset && (
              <span className="flex items-center gap-1">
                <Sunset size={12} /> {new Date(solar.sunset).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
              </span>
            )}
            {solar.day_length_hours && (
              <span>{solar.day_length_hours}h daylight</span>
            )}
          </div>
        )}
      </div>

      {/* Condition Banner */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="mx-4 mt-4"
      >
        <ConditionBadge
          variant="banner"
          score={currentBriefing.overall_score}
          assessment={currentBriefing.overall_assessment as ConditionAssessment}
          confidence={currentBriefing.confidence as "high" | "medium" | "low"}
          message={currentBriefing.ai_narrative || `Today's plan scores ${currentBriefing.overall_score}/100`}
          className="rounded-2xl p-4"
        />
      </motion.div>

      {/* Swap Banner */}
      {swaps.length > 0 && (
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="mx-4 mt-3 bg-amber/10 border border-amber/20 rounded-2xl p-4"
        >
          <div className="flex items-start gap-3">
            <AlertTriangle className="text-amber mt-0.5 shrink-0" size={20} />
            <div className="flex-1">
              <p className="font-semibold text-bark text-sm">Swap Suggested</p>
              <p className="text-stone text-xs mt-1">{swaps[0].reason}</p>
              <div className="flex gap-2 mt-3">
                <button
                  onClick={() => useCompanionStore.getState().handleSwap(tripId, swaps[0].id, "accept")}
                  className="bg-teal text-white px-4 py-1.5 rounded-lg text-xs font-semibold"
                >
                  Accept Swap
                </button>
                <button
                  onClick={() => useCompanionStore.getState().handleSwap(tripId, swaps[0].id, "decline")}
                  className="bg-cloud text-bark px-4 py-1.5 rounded-lg text-xs font-medium border border-bark/10"
                >
                  Keep Plan
                </button>
              </div>
            </div>
          </div>
        </motion.div>
      )}

      {/* Activity Cards */}
      <div className="px-4 mt-4 space-y-3">
        <h2 className="text-sm font-semibold text-bark uppercase tracking-wider">Activities</h2>
        {currentBriefing.activity_reports.map((report, i) => (
          <ActivityCard
            key={report.activity_id || i}
            report={report}
            isExpanded={expandedActivity === (report.activity_id || String(i))}
            onToggle={() =>
              setExpandedActivity(
                expandedActivity === (report.activity_id || String(i))
                  ? null
                  : (report.activity_id || String(i))
              )
            }
          />
        ))}
      </div>

      {/* Packing List */}
      {currentBriefing.packing_list.length > 0 && (
        <div className="px-4 mt-6">
          <h2 className="text-sm font-semibold text-bark uppercase tracking-wider mb-3">🎒 Today&apos;s Pack List</h2>
          <div className="bg-cloud rounded-2xl p-4 space-y-2">
            {currentBriefing.packing_list.map((item, i) => (
              <div key={i} className="flex items-center gap-2 text-sm text-bark">
                <CheckCircle2 size={14} className="text-leaf shrink-0" />
                <span>{item}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Hidden Gem */}
      {currentBriefing.hidden_gem && (
        <div className="px-4 mt-6">
          <div className="bg-gold/10 border border-gold/20 rounded-2xl p-4">
            <div className="flex items-center gap-2 mb-2">
              <Sparkles className="text-gold" size={18} />
              <span className="font-semibold text-bark text-sm">Hidden Gem</span>
            </div>
            <p className="text-stone text-sm">{currentBriefing.hidden_gem}</p>
          </div>
        </div>
      )}

      {/* Lookahead */}
      {currentBriefing.lookahead.length > 0 && (
        <div className="px-4 mt-6 mb-8">
          <h2 className="text-sm font-semibold text-bark uppercase tracking-wider mb-3">📅 Coming Up</h2>
          <div className="space-y-2">
            {currentBriefing.lookahead.map((day, i) => (
              <div key={i} className="bg-cloud rounded-xl p-3 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <ConditionBadge
                    variant="compact"
                    score={day.score}
                    assessment={day.assessment as ConditionAssessment}
                  />
                  <div>
                    <p className="text-sm font-medium text-bark">{day.date}</p>
                    <p className="text-xs text-stone">{day.summary} · {day.temp_range}</p>
                  </div>
                </div>
                {day.confidence !== "high" && (
                  <p className="text-[10px] text-driftwood">
                    {day.confidence === "medium" ? "May change" : "Too early"}
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      <BottomTabBar tripId={tripId} />
    </div>
  );
}

function ActivityCard({
  report,
  isExpanded,
  onToggle,
}: {
  report: ActivityReport;
  isExpanded: boolean;
  onToggle: () => void;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-cloud rounded-2xl overflow-hidden"
      style={{ boxShadow: "0 2px 8px rgba(44,62,80,0.06)" }}
    >
      <button onClick={onToggle} className="w-full p-4 text-left">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3 flex-1">
            <span className="text-lg">{report.emoji}</span>
            <div>
              <h3 className="font-semibold text-bark text-sm">{report.activity_name}</h3>
              {report.time_start && (
                <p className="text-xs text-stone font-mono mt-0.5">{report.time_start}–{report.time_end || "?"}</p>
              )}
            </div>
          </div>
          <div className="flex items-center gap-2">
            <ConditionBadge
              variant="compact"
              score={report.score}
              assessment={report.assessment as ConditionAssessment}
            />
            {isExpanded ? <ChevronUp size={16} className="text-stone" /> : <ChevronDown size={16} className="text-stone" />}
          </div>
        </div>
      </button>

      {isExpanded && (
        <motion.div
          initial={{ height: 0, opacity: 0 }}
          animate={{ height: "auto", opacity: 1 }}
          className="px-4 pb-4 border-t border-bark/5"
        >
          <div className="pt-3 space-y-3">
            {report.timing_suggestion && (
              <p className="text-sm text-teal flex items-center gap-2">
                <Eye size={14} /> {report.timing_suggestion}
              </p>
            )}

            {report.key_factors.length > 0 && (
              <div className="space-y-1">
                <p className="text-xs font-medium text-stone uppercase">Key Factors</p>
                {report.key_factors.map((f, i) => (
                  <p key={i} className="text-xs text-stone">{f.note}</p>
                ))}
              </div>
            )}

            {report.packing_suggestions.length > 0 && (
              <div className="space-y-1">
                <p className="text-xs font-medium text-stone uppercase">Pack for this</p>
                {report.packing_suggestions.map((item, i) => (
                  <p key={i} className="text-xs text-bark">• {item}</p>
                ))}
              </div>
            )}

            {report.pro_tips && report.pro_tips.length > 0 && (
              <div className="bg-teal/5 rounded-lg p-2">
                <p className="text-xs font-medium text-teal">💡 Pro Tip</p>
                {report.pro_tips.map((tip, i) => (
                  <p key={i} className="text-xs text-stone mt-1">{tip}</p>
                ))}
              </div>
            )}
          </div>
        </motion.div>
      )}
    </motion.div>
  );
}

function _getCurrentDayNumber(trip: { start_date?: string | null } | null): number {
  if (!trip?.start_date) return 1;
  const start = new Date(trip.start_date);
  const now = new Date();
  const diff = Math.floor((now.getTime() - start.getTime()) / (1000 * 60 * 60 * 24)) + 1;
  return Math.max(1, diff);
}
