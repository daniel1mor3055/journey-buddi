"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import { useParams, useRouter } from "next/navigation";
import mapboxgl from "mapbox-gl";
import "mapbox-gl/dist/mapbox-gl.css";
import { ArrowLeft, Compass } from "lucide-react";
import { useAuthStore } from "@/stores/auth-store";
import { useTripStore, ItineraryDay } from "@/stores/trip-store";
import { useCompanionStore, DayConditionReport } from "@/stores/companion-store";
import { BottomTabBar } from "@/components/layout/bottom-tab-bar";

const NZ_LOCATIONS: Record<string, [number, number]> = {
  Christchurch: [-43.532, 172.636],
  "Lake Tekapo": [-44.004, 170.477],
  "Mt Cook": [-43.735, 170.096],
  Wanaka: [-44.7, 169.132],
  Queenstown: [-45.031, 168.662],
  "Te Anau": [-45.414, 167.718],
  "Milford Sound": [-44.671, 167.926],
  Dunedin: [-45.874, 170.504],
  "Aoraki / Mt Cook": [-43.735, 170.096],
  "Franz Josef": [-43.389, 170.183],
  Hokitika: [-42.453, 170.968],
  Kaikoura: [-42.4, 173.681],
  "Abel Tasman": [-40.9, 173.0],
  Nelson: [-41.271, 173.284],
  Wellington: [-41.287, 174.776],
  Auckland: [-36.849, 174.764],
  Rotorua: [-38.137, 176.251],
  Taupo: [-38.686, 176.07],
  Tongariro: [-39.2, 175.6],
};

function resolveCoords(location: string): [number, number] | null {
  if (NZ_LOCATIONS[location]) return NZ_LOCATIONS[location];
  const key = Object.keys(NZ_LOCATIONS).find(
    (k) => location.toLowerCase().includes(k.toLowerCase()) || k.toLowerCase().includes(location.toLowerCase()),
  );
  return key ? NZ_LOCATIONS[key] : null;
}

function conditionColor(assessment?: string): string {
  switch (assessment?.toUpperCase()) {
    case "EXCELLENT":
    case "GOOD":
      return "#22C55E";
    case "FAIR":
      return "#F59E0B";
    case "POOR":
      return "#F97316";
    case "UNSAFE":
      return "#EF4444";
    default:
      return "#9CA3AF";
  }
}

function getCurrentDayNumber(trip: { start_date?: string | null } | null): number {
  if (!trip?.start_date) return 1;
  const start = new Date(trip.start_date);
  const now = new Date();
  const diff = Math.floor((now.getTime() - start.getTime()) / (1000 * 60 * 60 * 24)) + 1;
  return Math.max(1, diff);
}

interface DayPin {
  day: ItineraryDay;
  coords: [number, number]; // [lat, lon]
  condition?: DayConditionReport;
  isCurrent: boolean;
}

export default function MapPage() {
  const params = useParams();
  const router = useRouter();
  const tripId = params.tripId as string;

  const { isAuthenticated } = useAuthStore();
  const { currentTrip, itinerary, fetchItinerary } = useTripStore();
  const { conditions, fetchConditions } = useCompanionStore();

  const mapContainer = useRef<HTMLDivElement>(null);
  const mapRef = useRef<mapboxgl.Map | null>(null);
  const markersRef = useRef<mapboxgl.Marker[]>([]);
  const popupRef = useRef<mapboxgl.Popup | null>(null);
  const [mapLoaded, setMapLoaded] = useState(false);

  useEffect(() => {
    if (!isAuthenticated) {
      router.push("/auth");
      return;
    }
    if (tripId) {
      fetchItinerary(tripId);
      fetchConditions(tripId);
    }
  }, [tripId, isAuthenticated]);

  const buildPins = useCallback((): DayPin[] => {
    if (!itinerary?.days) return [];
    const currentDay = getCurrentDayNumber(currentTrip);
    return itinerary.days
      .map((day) => {
        const coords = resolveCoords(day.location);
        if (!coords) return null;
        const condition = conditions.find((c) => c.day_number === day.day_number);
        return {
          day,
          coords,
          condition,
          isCurrent: day.day_number === currentDay,
        } as DayPin;
      })
      .filter(Boolean) as DayPin[];
  }, [itinerary, conditions, currentTrip]);

  useEffect(() => {
    if (mapRef.current || !mapContainer.current) return;

    const token = process.env.NEXT_PUBLIC_MAPBOX_TOKEN;
    if (!token) return;

    mapboxgl.accessToken = token;
    const map = new mapboxgl.Map({
      container: mapContainer.current,
      style: "mapbox://styles/mapbox/outdoors-v12",
      center: [172.5, -41.5],
      zoom: 5,
    });

    map.addControl(new mapboxgl.NavigationControl(), "top-right");

    map.on("load", () => {
      setMapLoaded(true);
    });

    mapRef.current = map;

    return () => {
      map.remove();
      mapRef.current = null;
    };
  }, []);

  useEffect(() => {
    const map = mapRef.current;
    if (!map || !mapLoaded) return;

    markersRef.current.forEach((m) => m.remove());
    markersRef.current = [];
    if (popupRef.current) {
      popupRef.current.remove();
      popupRef.current = null;
    }

    const pins = buildPins();
    if (pins.length === 0) return;

    const routeCoords: [number, number][] = pins.map((p) => [p.coords[1], p.coords[0]]);

    if (map.getSource("route")) {
      (map.getSource("route") as mapboxgl.GeoJSONSource).setData({
        type: "Feature",
        properties: {},
        geometry: { type: "LineString", coordinates: routeCoords },
      });
    } else {
      map.addSource("route", {
        type: "geojson",
        data: {
          type: "Feature",
          properties: {},
          geometry: { type: "LineString", coordinates: routeCoords },
        },
      });
      map.addLayer({
        id: "route",
        type: "line",
        source: "route",
        layout: { "line-join": "round", "line-cap": "round" },
        paint: {
          "line-color": "#1B4332",
          "line-width": 3,
          "line-opacity": 0.6,
          "line-dasharray": [2, 2],
        },
      });
    }

    pins.forEach((pin) => {
      const color = conditionColor(pin.condition?.overall_assessment);
      const size = pin.isCurrent ? 18 : 12;
      const border = pin.isCurrent ? 4 : 2;

      const el = document.createElement("div");
      el.style.width = `${size * 2}px`;
      el.style.height = `${size * 2}px`;
      el.style.borderRadius = "50%";
      el.style.backgroundColor = color;
      el.style.border = `${border}px solid white`;
      el.style.boxShadow = "0 2px 6px rgba(0,0,0,0.3)";
      el.style.cursor = "pointer";
      el.style.display = "flex";
      el.style.alignItems = "center";
      el.style.justifyContent = "center";
      el.style.color = "white";
      el.style.fontWeight = "700";
      el.style.fontSize = pin.isCurrent ? "14px" : "11px";
      el.textContent = String(pin.day.day_number);

      if (pin.isCurrent) {
        el.style.animation = "pulse 2s infinite";
      }

      const activities = pin.day.activities.map((a) => {
        const activityReport = pin.condition?.activity_reports?.find(
          (r) => r.activity_name === a.name,
        );
        const score = activityReport?.score ?? a.condition_score;
        const assessment = activityReport?.assessment ?? null;
        return `
          <div style="display:flex;align-items:center;gap:6px;padding:3px 0;">
            <span style="font-size:14px;">${a.emoji}</span>
            <span style="flex:1;font-size:12px;color:#2C3E50;">${a.name}</span>
            ${score != null ? `<span style="font-size:11px;font-weight:600;color:${conditionColor(assessment ?? undefined)};">${score}</span>` : ""}
          </div>
        `;
      });

      const overallScore = pin.condition?.overall_score;
      const overallAssessment = pin.condition?.overall_assessment;

      const popupHtml = `
        <div style="min-width:180px;font-family:Inter,system-ui,sans-serif;">
          <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:6px;">
            <div>
              <div style="font-size:13px;font-weight:700;color:#1B4332;">
                Day ${pin.day.day_number} · ${pin.day.location}
              </div>
              ${pin.day.title ? `<div style="font-size:11px;color:#5D6D7E;margin-top:2px;">${pin.day.title}</div>` : ""}
            </div>
            ${
              overallScore != null
                ? `<div style="background:${conditionColor(overallAssessment)};color:white;border-radius:8px;padding:2px 8px;font-size:12px;font-weight:700;">
                    ${overallScore}
                  </div>`
                : ""
            }
          </div>
          ${
            overallAssessment
              ? `<div style="font-size:11px;color:${conditionColor(overallAssessment)};font-weight:600;margin-bottom:6px;">
                  ${overallAssessment}
                </div>`
              : ""
          }
          ${activities.length > 0 ? `<div style="border-top:1px solid #ECE5D8;padding-top:6px;">${activities.join("")}</div>` : ""}
        </div>
      `;

      const marker = new mapboxgl.Marker({ element: el })
        .setLngLat([pin.coords[1], pin.coords[0]])
        .addTo(map);

      el.addEventListener("click", () => {
        if (popupRef.current) popupRef.current.remove();
        const popup = new mapboxgl.Popup({ offset: size + 4, maxWidth: "260px" })
          .setLngLat([pin.coords[1], pin.coords[0]])
          .setHTML(popupHtml)
          .addTo(map);
        popupRef.current = popup;
      });

      markersRef.current.push(marker);
    });

    if (pins.length > 1) {
      const bounds = new mapboxgl.LngLatBounds();
      pins.forEach((p) => bounds.extend([p.coords[1], p.coords[0]]));
      map.fitBounds(bounds, { padding: 60, maxZoom: 10 });
    } else if (pins.length === 1) {
      map.flyTo({ center: [pins[0].coords[1], pins[0].coords[0]], zoom: 10 });
    }
  }, [mapLoaded, buildPins]);

  const isDataLoading = !itinerary;

  return (
    <div className="flex flex-col h-screen bg-mist">
      <div className="bg-forest text-white px-4 py-3 flex items-center gap-3 shrink-0 z-40">
        <button onClick={() => router.back()} className="p-1">
          <ArrowLeft size={20} className="text-white" />
        </button>
        <Compass size={18} className="text-white/70" />
        <h1 className="text-sm font-semibold text-white">Map View</h1>
      </div>

      <div className="flex-1 relative">
        {(isDataLoading || !mapLoaded) && (
          <div className="absolute inset-0 z-10 flex items-center justify-center bg-mist/80 backdrop-blur-sm">
            <div className="text-center">
              <Compass className="w-8 h-8 text-teal animate-spin mx-auto mb-3" />
              <p className="text-stone text-sm">Loading map...</p>
            </div>
          </div>
        )}
        <div ref={mapContainer} className="absolute inset-0" />
      </div>

      <style jsx global>{`
        @keyframes pulse {
          0%,
          100% {
            box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.5);
          }
          50% {
            box-shadow: 0 0 0 10px rgba(34, 197, 94, 0);
          }
        }
        .mapboxgl-popup-content {
          border-radius: 12px !important;
          padding: 12px !important;
          box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12) !important;
        }
        .mapboxgl-popup-close-button {
          font-size: 16px;
          padding: 4px 8px;
          color: #5d6d7e;
        }
      `}</style>

      <BottomTabBar tripId={tripId} />
    </div>
  );
}
