"use client";

import { cn } from "@/lib/utils";

export type ConditionAssessment =
  | "EXCELLENT"
  | "GOOD"
  | "FAIR"
  | "POOR"
  | "UNSAFE";

export type ConfidenceLevel = "high" | "medium" | "low";

export interface ConditionBadgeProps {
  score: number;
  assessment: ConditionAssessment;
  confidence?: ConfidenceLevel;
  message?: string;
  variant?: "compact" | "full" | "banner";
  className?: string;
}

const ASSESSMENT_CONFIG: Record<
  ConditionAssessment,
  { emoji: string; bgClass: string; textClass: string }
> = {
  EXCELLENT: {
    emoji: "🟢",
    bgClass: "bg-excellent/15",
    textClass: "text-excellent",
  },
  GOOD: {
    emoji: "🟡",
    bgClass: "bg-good/15",
    textClass: "text-good",
  },
  FAIR: {
    emoji: "🟠",
    bgClass: "bg-fair/15",
    textClass: "text-fair",
  },
  POOR: {
    emoji: "🔴",
    bgClass: "bg-poor/15",
    textClass: "text-poor",
  },
  UNSAFE: {
    emoji: "⛔",
    bgClass: "bg-unsafe/15",
    textClass: "text-unsafe",
  },
};

export function ConditionBadge({
  score,
  assessment,
  confidence = "high",
  message,
  variant = "full",
  className,
}: ConditionBadgeProps) {
  const config = ASSESSMENT_CONFIG[assessment];

  if (variant === "compact") {
    return (
      <span
        className={cn(
          "inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-sm font-medium",
          config.bgClass,
          config.textClass,
          className
        )}
      >
        <span aria-hidden>{config.emoji}</span>
        <span className="font-mono tabular-nums">{score}</span>
      </span>
    );
  }

  if (variant === "full") {
    return (
      <span
        className={cn(
          "inline-flex items-center gap-2 px-3 py-1.5 rounded-xl text-sm font-medium",
          config.bgClass,
          config.textClass,
          className
        )}
      >
        <span aria-hidden>{config.emoji}</span>
        <span>{assessment}</span>
        <span className="font-mono tabular-nums">{score}</span>
      </span>
    );
  }

  // banner variant
  return (
    <div
      className={cn(
        "flex flex-col gap-2 w-full px-4 py-3 rounded-xl",
        config.bgClass,
        config.textClass,
        className
      )}
    >
      <div className="flex flex-wrap items-center gap-2">
        <span aria-hidden>{config.emoji}</span>
        <span className="font-semibold">{assessment}</span>
        <span className="font-mono tabular-nums">{score}</span>
        {confidence !== "high" && (
          <span className="text-sm opacity-80">
            (confidence: {confidence})
          </span>
        )}
      </div>
      {message && (
        <p className="text-sm opacity-90">{message}</p>
      )}
    </div>
  );
}
