"use client";

import { useParams, useRouter } from "next/navigation";
import { ArrowLeft, Bell, Clock, Moon, LogOut, Shield, Compass } from "lucide-react";
import { useAuthStore } from "@/stores/auth-store";
import { BottomTabBar } from "@/components/layout/bottom-tab-bar";

export default function SettingsPage() {
  const params = useParams();
  const router = useRouter();
  const tripId = params.tripId as string;
  const { logout } = useAuthStore();

  const settingItems = [
    { icon: Bell, label: "Notification Preferences", desc: "Morning briefing time, quiet hours" },
    { icon: Clock, label: "Briefing Schedule", desc: "Configure when you receive briefings" },
    { icon: Moon, label: "Dark Mode", desc: "Coming soon" },
    { icon: Shield, label: "Emergency Info", desc: "NZ emergency contacts & nearby hospitals" },
  ];

  return (
    <div className="min-h-screen bg-mist pb-24">
      <div className="bg-forest text-white px-4 py-3 flex items-center gap-3 sticky top-0 z-40">
        <button onClick={() => router.back()} className="p-1">
          <ArrowLeft size={20} className="text-white" />
        </button>
        <h1 className="text-sm font-semibold text-white">Settings</h1>
      </div>

      <div className="max-w-lg mx-auto px-4 py-6 space-y-3">
        {settingItems.map((item) => {
          const Icon = item.icon;
          return (
            <div key={item.label} className="bg-cloud rounded-2xl p-4 flex items-center gap-4">
              <div className="w-10 h-10 rounded-xl bg-mist flex items-center justify-center">
                <Icon size={20} className="text-stone" />
              </div>
              <div className="flex-1">
                <p className="text-sm font-medium text-bark">{item.label}</p>
                <p className="text-xs text-stone">{item.desc}</p>
              </div>
            </div>
          );
        })}

        <button
          onClick={() => { logout(); router.replace("/"); }}
          className="w-full bg-cloud rounded-2xl p-4 flex items-center gap-4 text-left mt-6"
        >
          <div className="w-10 h-10 rounded-xl bg-poor/10 flex items-center justify-center">
            <LogOut size={20} className="text-poor" />
          </div>
          <div className="flex-1">
            <p className="text-sm font-medium text-poor">Log Out</p>
            <p className="text-xs text-stone">Sign out of your account</p>
          </div>
        </button>
      </div>

      <BottomTabBar tripId={tripId} />
    </div>
  );
}
