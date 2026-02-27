"use client";

import { useParams, useRouter } from "next/navigation";
import { ArrowLeft, Map as MapIcon } from "lucide-react";
import { BottomTabBar } from "@/components/layout/bottom-tab-bar";

export default function MapPage() {
  const params = useParams();
  const router = useRouter();
  const tripId = params.tripId as string;

  return (
    <div className="min-h-screen bg-mist pb-24">
      <div className="bg-forest text-white px-4 py-3 flex items-center gap-3 sticky top-0 z-40">
        <button onClick={() => router.back()} className="p-1">
          <ArrowLeft size={20} className="text-white" />
        </button>
        <h1 className="text-sm font-semibold text-white">Map View</h1>
      </div>

      <div className="flex flex-col items-center justify-center min-h-[60vh] px-8 text-center">
        <MapIcon className="w-16 h-16 text-driftwood mb-4" />
        <h2 className="text-lg font-semibold text-bark mb-2">Map Coming Soon</h2>
        <p className="text-stone text-sm max-w-sm">
          Interactive map with your route, attraction pins color-coded by condition status,
          and current location tracking will be available here.
        </p>
      </div>

      <BottomTabBar tripId={tripId} />
    </div>
  );
}
