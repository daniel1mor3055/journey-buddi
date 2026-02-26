"use client";

import Link from "next/link";
import Image from "next/image";
import { motion } from "framer-motion";
import { ChevronDown, Compass, MessageCircle, Calendar, Map as MapIcon } from "lucide-react";

const NZ_IMAGES = {
  hero: "https://images.unsplash.com/photo-1567924611412-2caab2b207fb?w=1200&q=80",
  queenstown: "https://images.unsplash.com/photo-1592275142354-0d765e9a9c42?w=1200&q=80",
  waterfall: "https://images.unsplash.com/photo-1580466285541-d8f12ea3d21b?w=800&q=80",
};

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-mist">
      {/* Hero Section */}
      <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
        <div className="absolute inset-0">
          <Image
            src={NZ_IMAGES.hero}
            alt="Milford Sound, New Zealand"
            fill
            className="object-cover"
            priority
          />
          <div
            className="absolute inset-0"
            style={{
              background:
                "linear-gradient(to top, rgba(27,67,50,0.85) 0%, rgba(27,67,50,0.4) 40%, rgba(27,67,50,0.2) 100%)",
            }}
          />
        </div>

        <div className="relative z-10 text-center px-6 max-w-xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, ease: "easeOut" }}
          >
            <div className="flex items-center justify-center gap-2 mb-6">
              <div className="w-10 h-10 rounded-full bg-teal flex items-center justify-center">
                <Compass className="text-white" size={22} />
              </div>
              <span className="text-white text-2xl font-bold tracking-tight">
                Journey Buddi
              </span>
            </div>

            <h1 className="text-white mb-4 text-4xl font-bold leading-tight">
              Your AI Travel Companion
            </h1>

            <p className="text-white/90 mb-8 text-base leading-relaxed">
              Plan the perfect adventure. Adapt when conditions change. Discover
              stories behind every place. Experience everything at its absolute
              best.
            </p>

            <Link
              href="/auth"
              className="block w-full bg-teal text-white rounded-xl py-4 px-8 text-lg font-semibold transition-all hover:shadow-lg active:scale-[0.98] text-center"
              style={{ minHeight: 52 }}
            >
              Start Planning — Free
            </Link>

            <p className="text-white/60 mt-3 text-xs">No account needed</p>
          </motion.div>

          <motion.div
            className="absolute bottom-8 left-1/2 -translate-x-1/2"
            animate={{ y: [0, 8, 0] }}
            transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
          >
            <ChevronDown className="text-white/50" size={28} />
          </motion.div>
        </div>
      </section>

      {/* Value Props */}
      <section className="px-4 py-16 lg:py-24 max-w-6xl mx-auto">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {[
            {
              emoji: "🧠",
              title: "Save 20+ Hours",
              desc: "Chat with Buddi, get a complete itinerary in minutes. Compare providers, see reviews, book everything.",
            },
            {
              emoji: "🌤️",
              title: "See Everything at Its Best",
              desc: "Buddi monitors conditions and shuffles your plan so you kayak on calm days and hike in clear skies.",
            },
            {
              emoji: "📖",
              title: "Hear the Stories",
              desc: "Every place has a story. Listen to legends while you walk, learn the geology while you drive.",
            },
            {
              emoji: "💰",
              title: "Save Money Like a Local",
              desc: "Insider discounts, the best apps, cheaper fuel, early-bird deals. Tips only seasoned travelers know.",
            },
          ].map((vp, i) => (
            <motion.div
              key={vp.title}
              className="bg-cloud rounded-2xl p-6 shadow-sm"
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: i * 0.1 }}
            >
              <div className="text-3xl mb-3">{vp.emoji}</div>
              <h3 className="text-bark mb-2 text-lg font-semibold">{vp.title}</h3>
              <p className="text-stone text-sm leading-relaxed">{vp.desc}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* How It Works */}
      <section className="px-4 py-16 bg-sand/50">
        <div className="max-w-3xl mx-auto">
          <h2 className="text-center text-bark mb-12 text-3xl font-bold">
            How It Works
          </h2>
          <div className="space-y-8">
            {[
              {
                step: 1,
                icon: MessageCircle,
                title: "Chat with Buddi",
                desc: "Tell Buddi your style, group, interests, and must-dos. Pick from curated options — takes 10 minutes.",
              },
              {
                step: 2,
                icon: Calendar,
                title: "Get Your Trip Dashboard",
                desc: "An interactive itinerary you can edit, with bookings, maps, conditions, stories, and hidden gems.",
              },
              {
                step: 3,
                icon: MapIcon,
                title: "Travel with a Companion",
                desc: "Morning briefings, condition alerts, smart day shuffles, audio stories, and a treasure map of hidden gems.",
              },
            ].map((s, i) => (
              <motion.div
                key={s.step}
                className="flex gap-5 items-start"
                initial={{ opacity: 0, x: -20 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: i * 0.15 }}
              >
                <div className="w-12 h-12 rounded-2xl bg-forest text-white flex items-center justify-center shrink-0 font-bold text-lg">
                  {s.step}
                </div>
                <div>
                  <h3 className="text-bark mb-1 text-lg font-semibold">
                    {s.title}
                  </h3>
                  <p className="text-stone text-[0.9375rem] leading-relaxed">
                    {s.desc}
                  </p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Dashboard Showcase */}
      <section className="px-4 py-16 lg:py-24 max-w-6xl mx-auto">
        <div className="lg:flex lg:items-center lg:gap-12">
          <div className="lg:w-1/2 mb-8 lg:mb-0">
            <motion.h2
              className="text-bark mb-4 text-3xl font-bold"
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
            >
              Your Trip Command Center
            </motion.h2>
            <p className="text-stone mb-6 leading-relaxed">
              Every detail, every booking, every condition — tappable, editable,
              actionable. Not a static PDF. A living dashboard that adapts with
              your trip.
            </p>
            <div className="space-y-3">
              {[
                "Interactive day cards with booking status",
                "Real-time condition monitoring",
                "Hidden gems & insider tips",
                "One-tap navigation & calls",
              ].map((f) => (
                <div
                  key={f}
                  className="flex items-center gap-2 text-bark text-[0.9375rem]"
                >
                  <span className="text-leaf">✓</span> {f}
                </div>
              ))}
            </div>
          </div>
          <div className="lg:w-1/2">
            <DashboardPreviewCard />
          </div>
        </div>
      </section>

      {/* Destination Teaser & Final CTA */}
      <section className="relative py-20 overflow-hidden">
        <div className="absolute inset-0">
          <Image
            src={NZ_IMAGES.queenstown}
            alt="Queenstown, New Zealand"
            fill
            className="object-cover"
          />
          <div className="absolute inset-0 bg-forest/80" />
        </div>
        <div className="relative z-10 text-center px-6 max-w-lg mx-auto">
          <h2 className="text-white mb-2 text-3xl font-bold">
            Pilot Destination: New Zealand
          </h2>
          <p className="text-white/80 mb-2">
            18 days of glaciers, whales, fiords, volcanoes, and the world&apos;s
            best adventure activities.
          </p>
          <p className="text-white/60 mb-8 text-sm">
            More destinations coming soon
          </p>
          <Link
            href="/auth"
            className="block w-full max-w-sm mx-auto bg-teal text-white rounded-xl py-4 px-8 text-lg font-semibold transition-all hover:shadow-lg active:scale-[0.98] text-center"
          >
            Start Planning Your NZ Trip
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-forest px-6 py-12 text-white/60 text-sm">
        <div className="max-w-6xl mx-auto text-center">
          <div className="flex items-center justify-center gap-2 mb-4">
            <Compass size={18} className="text-teal" />
            <span className="text-white font-semibold">Journey Buddi</span>
          </div>
          <p className="mb-2">AI-powered adaptive travel companion</p>
          <p className="text-xs">Made with care for intentional explorers</p>
        </div>
      </footer>
    </div>
  );
}

function DashboardPreviewCard() {
  return (
    <div className="mx-auto w-[300px] lg:w-[320px]">
      <div
        className="bg-bark rounded-[2.5rem] p-3"
        style={{ boxShadow: "0 8px 32px rgba(44,62,80,0.2)" }}
      >
        <div className="bg-mist rounded-[2rem] overflow-hidden">
          <div className="h-6 bg-bark flex items-center justify-center">
            <div className="w-20 h-3 bg-mist/20 rounded-full" />
          </div>
          <div className="max-h-[480px] overflow-hidden p-3 text-xs">
            <div className="bg-forest rounded-lg p-2 mb-2 text-white text-center text-[0.65rem] font-semibold">
              NZ South Island — 18 Days
            </div>
            <div className="bg-sand rounded-lg p-2 mb-2 text-center text-stone text-[0.55rem]">
              ✅ 6 booked · ⚠️ 4 need booking · 2 flex
            </div>
            {[
              { day: 1, loc: "Christchurch", acts: "✈️ Arrive 2:30 PM", score: 92, color: "#D4EDDA" },
              { day: 2, loc: "Kaikoura", acts: "🐬✅ · 🐋⚠️ · 🦭✅", score: 88, color: "#D4EDDA" },
              { day: 7, loc: "Abel Tasman", acts: "🛶⚠️ · 🥾✅", score: 54, color: "#FFF3E0" },
            ].map((d) => (
              <div key={d.day} className="bg-cloud rounded-lg p-2 mb-1.5 shadow-sm">
                <div className="flex justify-between items-center mb-1">
                  <span className="text-bark font-semibold text-[0.65rem]">
                    Day {d.day} · {d.loc}
                  </span>
                  <span
                    className="px-1.5 py-0.5 rounded-full text-[0.5rem] font-mono"
                    style={{ background: d.color }}
                  >
                    {d.score > 70 ? "🟢" : "🟠"} {d.score}
                  </span>
                </div>
                <p className="text-stone text-[0.55rem]">{d.acts}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
