"use client";

import { usePathname, useRouter } from "next/navigation";
import { Compass, CalendarDays, MessageCircle, Map, MoreHorizontal } from "lucide-react";
import { cn } from "@/lib/utils";

interface TabItem {
  label: string;
  icon: typeof Compass;
  href: string;
  matchPrefix: string;
}

export function BottomTabBar({ tripId }: { tripId: string }) {
  const pathname = usePathname();
  const router = useRouter();

  const tabs: TabItem[] = [
    { label: "Today", icon: Compass, href: `/trip/${tripId}/today`, matchPrefix: `/trip/${tripId}/today` },
    { label: "Trip", icon: CalendarDays, href: `/trip/${tripId}`, matchPrefix: `/trip/${tripId}` },
    { label: "Chat", icon: MessageCircle, href: `/trip/${tripId}/chat`, matchPrefix: `/trip/${tripId}/chat` },
    { label: "Map", icon: Map, href: `/trip/${tripId}/map`, matchPrefix: `/trip/${tripId}/map` },
    { label: "More", icon: MoreHorizontal, href: `/trip/${tripId}/settings`, matchPrefix: `/trip/${tripId}/settings` },
  ];

  const isActive = (tab: TabItem) => {
    if (tab.label === "Trip") {
      return pathname === `/trip/${tripId}` || pathname.startsWith(`/trip/${tripId}/day`);
    }
    return pathname.startsWith(tab.matchPrefix);
  };

  return (
    <div className="fixed bottom-0 left-0 right-0 z-50 bg-cloud border-t border-bark/10"
      style={{ paddingBottom: "env(safe-area-inset-bottom)" }}
    >
      <div className="flex items-center justify-around max-w-lg mx-auto px-2 py-2">
        {tabs.map((tab) => {
          const active = isActive(tab);
          const Icon = tab.icon;
          return (
            <button
              key={tab.label}
              onClick={() => router.push(tab.href)}
              className={cn(
                "flex flex-col items-center gap-0.5 px-3 py-1.5 rounded-lg transition-colors min-w-[56px]",
                active ? "text-forest" : "text-driftwood"
              )}
            >
              <Icon size={20} strokeWidth={active ? 2.5 : 2} />
              <span className={cn("text-[10px]", active ? "font-semibold" : "font-medium")}>
                {tab.label}
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
