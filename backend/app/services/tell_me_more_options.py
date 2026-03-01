"""
'Tell me more first' response options for the GREETING step.

To switch the active response, change ACTIVE_TELL_ME_MORE below.
"""

# ── Option A: Full version (currently active) ────────────────────────────────

TELL_ME_MORE_FULL = (
    "Journey Buddi is an AI-powered adaptive travel companion that transforms how you plan and experience extended trips. "
    "Instead of leaving you to manage a rigid, static spreadsheet or browse generic booking catalogs, "
    "it acts as the knowledgeable, local expert friend you wish you had traveling with you.\n\n"
    "Here's how it works in two phases:\n\n"
    "🗺️ Phase 1 — The Pre-Trip Travel Architect\n"
    "You don't fill out tedious forms. Instead, you have a structured conversation with me. "
    "I ask you to make concrete choices about your adventure level, pace, and interests — "
    "then do the heavy lifting: a complete day-by-day itinerary with optimized driving routes, "
    "balanced activity loads, and built-in flexibility.\n\n"
    "🌍 Phase 2 — The Adaptive Live Companion\n"
    "This is where I truly differ from TripAdvisor, GetYourGuide, and every other travel tool. "
    "Once you're traveling, your itinerary becomes a living plan that evolves with real-world conditions:\n\n"
    "⛅ Real-Time Condition Swaps — I monitor weather, wind, tides, and aurora activity. "
    "If dangerous winds threaten your alpine hike, I'll proactively swap it with a better-weather day "
    "and give you step-by-step instructions to adjust your plans and bookings.\n\n"
    "☀️ Actionable Daily Briefings — Every morning, a 2–3 minute briefing tells you exactly what to expect for the day.\n\n"
    "🎒 Hyper-Specific Preparation — No generic \"dress in layers\" advice. "
    "I give you exact packing lists based on today's actual forecast "
    "(e.g., bring a windproof shell and beanie — summit wind chill hits -1°C at 11 AM).\n\n"
    "🔍 Insider Local Knowledge — The optimal time to arrive to beat crowds, "
    "hidden viewpoints most tourists walk past, and audio stories about local history, geology, and legends.\n\n"
    "Ultimately, I'm here to eliminate the stress of planning and adapting on the fly — "
    "so you experience everything in the absolute best possible conditions.\n\n"
    "Ready to build your trip?"
)

# ── Option B: Short version ───────────────────────────────────────────────────

TELL_ME_MORE_SHORT = (
    "Journey Buddi is an AI-powered adaptive travel companion that transforms how you plan and experience extended trips. "
    "Instead of leaving you to manage a rigid spreadsheet, it acts as a knowledgeable local expert "
    "traveling with you in two main phases:\n\n"
    "🗺️ Phase 1 — The Pre-Trip Travel Architect\n"
    "Instead of filling out tedious forms, you have a guided conversation with me about your interests, "
    "adventure level, and preferred pace. I then do the heavy lifting — building a complete, day-by-day "
    "itinerary that optimizes your driving routes and balances your activities.\n\n"
    "🌍 Phase 2 — The Adaptive Live Companion\n"
    "Once you start traveling, your itinerary becomes a living plan that continuously evolves "
    "based on real-time weather, wind, and tides.\n\n"
    "⛅ Proactive Swaps — If bad weather threatens a key activity, I'll suggest swapping it to a better day "
    "and give you step-by-step instructions on how to adjust your plans.\n\n"
    "☀️ Actionable Daily Briefings — Every morning, a condition assessment and exact packing lists "
    "based on the actual forecast — replacing generic \"dress in layers\" advice.\n\n"
    "🔍 Local Insider Tips — Optimal arrival times to beat crowds, hidden viewpoints, and local stories "
    "for every stop.\n\n"
    "Ultimately, Journey Buddi eliminates the stress of planning and adapting on the fly — "
    "ensuring you experience everything in the absolute best possible conditions.\n\n"
    "Ready to build your trip?"
)

# ── Active selection ──────────────────────────────────────────────────────────
# Switch to TELL_ME_MORE_SHORT to use the shorter version.

ACTIVE_TELL_ME_MORE = TELL_ME_MORE_FULL
