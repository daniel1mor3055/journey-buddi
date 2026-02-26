"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { Compass, Plus, LogOut, Map as MapIcon } from "lucide-react";
import { useAuthStore } from "@/stores/auth-store";

export default function DashboardPage() {
  const router = useRouter();
  const { user, isAuthenticated, isLoading, initialize, logout } =
    useAuthStore();

  useEffect(() => {
    initialize();
  }, [initialize]);

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.replace("/auth");
    }
  }, [isLoading, isAuthenticated, router]);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-mist flex items-center justify-center">
        <div className="text-stone">Loading...</div>
      </div>
    );
  }

  if (!isAuthenticated || !user) return null;

  return (
    <div className="min-h-screen bg-mist">
      {/* Header */}
      <header className="bg-forest text-white px-4 py-3 flex items-center justify-between sticky top-0 z-40">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-full bg-teal flex items-center justify-center">
            <Compass className="text-white" size={18} />
          </div>
          <span className="font-bold text-lg">Journey Buddi</span>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-white/70 text-sm hidden sm:block">
            {user.email}
          </span>
          <button
            onClick={() => {
              logout();
              router.replace("/");
            }}
            className="p-2 rounded-lg bg-white/10 hover:bg-white/20 transition-colors"
            title="Log out"
          >
            <LogOut size={18} />
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 py-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <h1 className="text-bark mb-2 text-2xl font-bold">
            Welcome{user.name ? `, ${user.name}` : ""}!
          </h1>
          <p className="text-stone mb-8">
            Ready to plan your next adventure? Start a new trip or continue
            where you left off.
          </p>

          {/* Empty State */}
          <div
            className="bg-cloud rounded-2xl p-8 text-center"
            style={{ boxShadow: "0 2px 8px rgba(44,62,80,0.06)" }}
          >
            <div className="w-20 h-20 rounded-full bg-sand flex items-center justify-center mx-auto mb-4">
              <MapIcon size={36} className="text-driftwood" />
            </div>
            <h3 className="text-bark mb-2 text-lg font-semibold">
              No trips yet
            </h3>
            <p className="text-stone mb-6 text-sm max-w-sm mx-auto">
              Chat with Buddi to plan your first trip. Start with New Zealand —
              our pilot destination with 18 days of incredible experiences.
            </p>
            <button className="bg-teal text-white rounded-xl py-3 px-8 font-semibold transition-all hover:shadow-md active:scale-[0.98] inline-flex items-center gap-2">
              <Plus size={20} />
              Plan a New Trip
            </button>
          </div>
        </motion.div>
      </main>
    </div>
  );
}
