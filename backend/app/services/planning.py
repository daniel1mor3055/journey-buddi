"""Planning conversation state machine.

Manages the structured flow:
Round 1 (Travel DNA): GREETING → GROUP → AGE_RANGE → ACCESSIBILITY → FITNESS
Round 2+ (Logistics, Interests, etc.): DATES → DRIVING → FLIGHTS → INTERESTS → ...
"""
from __future__ import annotations

import json
from typing import Optional

import structlog

from app.services.openai_client import openai_client as gemini_client
from app.services.tell_me_more_options import ACTIVE_TELL_ME_MORE

log = structlog.get_logger()

PLANNING_STEPS = [
    "GREETING",
    # Round 1: Travel DNA
    "GROUP",
    "AGE_RANGE",
    "ACCESSIBILITY",
    "FITNESS",
    # Round 2+: Logistics, Interests, Deep Dive, Route
    "DATES",
    "DRIVING",
    "FLIGHTS",
    "INTERESTS",
    "MUST_DOS",
    "PROVIDERS",
    "AUTONOMOUS",
    "GENERATING",
    "CONFIRMED",
]

FREE_TEXT_STEPS = frozenset({"AGE_RANGE"})

STEP_INDEX = {step: i for i, step in enumerate(PLANNING_STEPS)}

SYSTEM_PROMPT = """You are Buddi, an expert travel companion AI built into the Journey Buddi app.
You are helping a traveler plan an extended New Zealand trip.

PERSONALITY:
- You are warm, knowledgeable, and opinionated — you have clear recommendations
- You speak conversationally, like a well-traveled friend
- You are specific and practical, never vague
- You are honest — if something isn't great, you say so gently
- You are enthusiastic about travel without being cheesy

RULES:
- NEVER ask open-ended questions. Always present concrete options for the user to choose from.
- When presenting options, limit to 3-5 choices maximum.
- Always have a recommendation — "I'd suggest X because Y"
- Acknowledge the user's previous choice before moving forward.
- Keep responses concise — travelers don't want to read essays.
- Use emoji sparingly: weather icons, activity icons, status indicators only.
- When you don't know something with certainty, say so.

OUTPUT FORMAT:
Always respond with valid JSON matching the schema below. No markdown fences.

{
  "text": "Your conversational message to the user",
  "choices": [
    {"emoji": "🏖️", "label": "Option name", "desc": "Brief description"}
  ],
  "multi_select": false,
  "free_text": false,
  "provider_cards": null
}

For free-text steps (where the user types a response instead of choosing from options),
set "choices" to null and "free_text" to true.

If the step requires provider comparison cards, use:
{
  "text": "Your message",
  "choices": null,
  "provider_cards": [
    {"emoji": "🏆", "name": "Provider", "location": "City", "rating": 4.9, "reviews": 1890, "price": 275, "whatsSpecial": "Description", "buddiPick": true}
  ]
}
"""


def get_step_prompt(step: str, planning_state: dict) -> str:
    """Generate a step-specific instruction to append to the system prompt."""
    prompts = {
        "GREETING": (
            "Greet the user warmly. Introduce yourself as Buddi. "
            "Tell them you'll help plan an incredible NZ adventure in about 10 minutes. "
            "Present two choices: 'Let's do it!' and 'Tell me more first'."
        ),
        "GROUP": (
            "This is the FIRST planning question. Ask who's coming along on this adventure. "
            "Present exactly 4 options: "
            "'Flying solo' (just me and the open road), "
            "'With my partner' (adventure for two), "
            "'Family trip' (kids are coming along), "
            "'Friends trip' (the crew is rolling deep). "
            "Use appropriate emoji for each."
        ),
        "AGE_RANGE": (
            "This is a FREE TEXT step — set choices to null and free_text to true. "
            "Based on the user's group selection, ask about the ages of everyone traveling. "
            "Make it conversational and explain WHY you're asking (e.g., helps with pacing, "
            "activity suitability, etc.). Examples by group type: "
            "Solo → ask their age or age range. "
            "Couple → ask the age range for both. "
            "Family → ask how old the kids are, mention it helps with pacing and rest stops. "
            "Friends → ask the age range of the group. "
            f"Group type selected: {planning_state.get('group_type', 'unknown')}. "
            "Acknowledge their group choice first."
        ),
        "ACCESSIBILITY": (
            "Ask about accessibility requirements for the group. "
            "Frame it naturally — e.g., 'Does anyone in your group have accessibility requirements?' "
            "Present exactly 3 options: "
            "'No accessibility needs' (no restrictions, full range of NZ activities), "
            "'Travelling with stroller/pram' (need pram-friendly paths, accommodation & vehicles), "
            "'Wheelchair or mobility aid' (need fully accessible facilities throughout). "
            "Use appropriate emoji for each. Acknowledge their previous answer first."
        ),
        "FITNESS": (
            "Ask about the maximum comfortable hiking level for the group. "
            "Ask about their energy levels for the trip, framed around pacing their days — not just hiking. "
            "Tailor the framing to their group type "
            f"(group: {planning_state.get('group_type', 'unknown')}, "
            f"ages: {planning_state.get('age_range', 'unknown')}). "
            "Present exactly 4 options with these labels and descriptions: "
            "'Keep it relaxed' (scenic drives, flat strolls, frequent stops — up to an hour of walking a day), "
            "'Active explorer' (on their feet for a few hours exploring towns, beaches, or undulating paths, but needs time to recharge), "
            "'Endless energy' (highly physical days, steep climbs, full-day excursions — no problem), "
            "'A mix of everything' (push occasionally, balanced with easy recovery days). "
            "Acknowledge their accessibility answer first."
        ),
        "DATES": (
            "Ask when they're thinking of visiting NZ. Suggest 3-4 date ranges "
            "plus a 'Flexible' option. Acknowledge their group choice first."
        ),
        "DRIVING": (
            "Ask about driving comfort level. Present 3 options: "
            "Short (1-2 hours max/day), 3-4 hours is fine, 5+ hours is OK. "
            "Acknowledge their date choice first."
        ),
        "FLIGHTS": (
            "Ask if they have flights booked. Present 3 options: "
            "Yes (I have details), Not yet (I'll add later), Help me figure it out. "
            "Acknowledge their driving preference first."
        ),
        "INTERESTS": (
            "Ask what types of experiences excite them. This is a MULTI-SELECT step. "
            "Set multi_select to true. Present 8 interest categories: "
            "Mountains & Hiking, Ocean & Marine, Food & Wine, Photography, "
            "Adrenaline, Nature & Wildlife, Culture & History, Stargazing. "
            "Acknowledge their flight info first."
        ),
        "MUST_DOS": (
            "Based on their interests, ask about absolute must-dos. MULTI-SELECT. "
            "Set multi_select to true. Present 6-8 popular NZ attractions matching their interests. "
            "Acknowledge their interests first."
        ),
        "PROVIDERS": (
            f"Based on the user's interest in activities, present provider comparison cards "
            f"for one of their must-do activities. Use provider_cards format. "
            f"Include 2-3 providers with ratings, prices, and a Buddi pick. "
            f"Current selections: {json.dumps(planning_state.get('must_dos', []))}. "
            f"Acknowledge their must-dos first."
        ),
        "AUTONOMOUS": (
            "Almost done! Ask if they want Buddi to handle the day-by-day ordering "
            "or if they want to sequence things themselves. Present 2 options: "
            "'You decide (I trust you, Buddi!)' and 'Let me see options first'. "
            "Acknowledge their provider selection first."
        ),
        "GENERATING": (
            "The trip is being generated! Tell the user excitedly that their trip is ready. "
            "Give a preview of the first 3 days of their NZ itinerary. "
            "Make it specific and exciting based on their selections: "
            f"{json.dumps(planning_state)}."
        ),
    }
    return prompts.get(step, "Continue the conversation naturally.")


TELL_ME_MORE_RESPONSE: dict = {
    "text": ACTIVE_TELL_ME_MORE,
    "choices": [
        {"emoji": "🎯", "label": "Let's do it!", "desc": ""},
    ],
    "multi_select": False,
}

_TELL_ME_MORE_LABELS = frozenset({"Tell me more first", "Tell me more"})


def is_tell_me_more(step: str, user_input: str) -> bool:
    """Check if the user chose 'Tell me more' during GREETING."""
    return step == "GREETING" and user_input.strip() in _TELL_ME_MORE_LABELS


def progress_percent(step: str) -> float:
    idx = STEP_INDEX.get(step, 0)
    return round((idx / (len(PLANNING_STEPS) - 1)) * 100, 1)


def next_step(current: str) -> Optional[str]:
    idx = STEP_INDEX.get(current)
    if idx is None or idx >= len(PLANNING_STEPS) - 1:
        return None
    return PLANNING_STEPS[idx + 1]


def prev_step(current: str) -> Optional[str]:
    idx = STEP_INDEX.get(current)
    if idx is None or idx <= 0:
        return None
    return PLANNING_STEPS[idx - 1]


def update_planning_state(state: dict, step: str, user_input: str) -> dict:
    """Extract structured data from user input and update planning state."""
    updated = {**state}

    field_map = {
        "GROUP": "group_type",
        "AGE_RANGE": "age_range",
        "ACCESSIBILITY": "accessibility",
        "FITNESS": "fitness_level",
        "DATES": "travel_dates",
        "DRIVING": "driving_preference",
        "FLIGHTS": "flights_status",
        "INTERESTS": "interests",
        "MUST_DOS": "must_dos",
        "PROVIDERS": "provider_selection",
        "AUTONOMOUS": "planning_mode",
    }

    field = field_map.get(step)
    if field:
        if step in ("INTERESTS", "MUST_DOS"):
            updated[field] = [s.strip() for s in user_input.split(",") if s.strip()]
        else:
            updated[field] = user_input

    updated["current_step"] = step
    return updated


async def generate_step_response(
    step: str,
    planning_state: dict,
    user_message: Optional[str] = None,
    conversation_history: Optional[list] = None,
) -> dict:
    """Generate the AI response for a given planning step."""
    step_instruction = get_step_prompt(step, planning_state)
    full_system = (
        SYSTEM_PROMPT
        + f"\n\nCURRENT PLANNING STATE:\n{json.dumps(planning_state)}"
        + f"\n\nCURRENT STEP: {step}\nINSTRUCTION: {step_instruction}"
    )

    prompt = user_message or f"Start the {step} step of the planning conversation."

    result = await gemini_client.generate_json(
        system_prompt=full_system,
        user_message=prompt,
        conversation_history=conversation_history,
    )

    if not result or "text" not in result:
        return _fallback_step_response(step, planning_state)

    return result


def _fallback_step_response(step: str, planning_state: dict) -> dict:
    """Hardcoded fallback responses when AI is unavailable."""
    fallbacks = {
        "GREETING": {
            "text": "Hey there! 👋 I'm Buddi, your travel companion. I'm going to help you plan an incredible New Zealand adventure — one that adapts to conditions, saves you money, and shows you things most tourists miss.\n\nLet's start by getting to know your travel style. This takes about 10 minutes and saves you 20+ hours of research. Ready?",
            "choices": [
                {"emoji": "🎯", "label": "Let's do it!", "desc": ""},
                {"emoji": "🗺️", "label": "Tell me more first", "desc": ""},
            ],
            "multi_select": False,
        },
        "GROUP": {
            "text": "First up — who's coming along on this adventure?",
            "choices": [
                {"emoji": "🧑", "label": "Flying solo", "desc": "Just me and the open road"},
                {"emoji": "💑", "label": "With my partner", "desc": "Adventure for two"},
                {"emoji": "👨‍👩‍👧‍👦", "label": "Family trip", "desc": "Kids are coming along"},
                {"emoji": "👯", "label": "Friends trip", "desc": "The crew is rolling deep"},
            ],
            "multi_select": False,
        },
        "AGE_RANGE": {
            "text": "Great! To make sure I recommend the right activities and pace, what are the ages of everyone traveling?",
            "choices": None,
            "free_text": True,
            "multi_select": False,
        },
        "ACCESSIBILITY": {
            "text": "Does anyone in your group have accessibility requirements?",
            "choices": [
                {"emoji": "✅", "label": "No accessibility needs", "desc": "No restrictions — full range of activities"},
                {"emoji": "🍼", "label": "Travelling with stroller/pram", "desc": "Need pram-friendly paths, accommodation & vehicles"},
                {"emoji": "♿", "label": "Wheelchair or mobility aid", "desc": "Need fully accessible facilities throughout"},
            ],
            "multi_select": False,
        },
        "FITNESS": {
            "text": "To help me pace our days perfectly, let's talk about your energy levels. What does a comfortable day of exploring look like for you?",
            "choices": [
                {"emoji": "🛋️", "label": "Keep it relaxed", "desc": "Scenic drives, flat strolls, frequent stops. Up to an hour of walking a day."},
                {"emoji": "🥾", "label": "Active explorer", "desc": "A few hours on my feet — towns, beaches, gentle hills. Need time to recharge."},
                {"emoji": "🔥", "label": "Endless energy", "desc": "Steep climbs, full-day excursions — bring it on."},
                {"emoji": "🎲", "label": "A mix of everything", "desc": "Push occasionally, balanced with easy recovery days."},
            ],
            "multi_select": False,
        },
        "DATES": {
            "text": "Perfect! When are you thinking of visiting New Zealand?",
            "choices": [
                {"emoji": "🗓️", "label": "Dec 5–22", "desc": "18 days, summer"},
                {"emoji": "📅", "label": "Jan 2026", "desc": "Peak summer"},
                {"emoji": "🌸", "label": "Mar 2026", "desc": "Autumn colours"},
                {"emoji": "🤷", "label": "Flexible", "desc": "Help me pick!"},
            ],
            "multi_select": False,
        },
        "DRIVING": {
            "text": "How do you feel about driving?",
            "choices": [
                {"emoji": "🐢", "label": "Short", "desc": "1-2 hours max per day"},
                {"emoji": "🚗", "label": "3-4 hours is fine", "desc": "Road trips are part of the fun"},
                {"emoji": "🏎️", "label": "5+ hours is OK", "desc": "See as much as possible"},
            ],
            "multi_select": False,
        },
        "FLIGHTS": {
            "text": "Got your flights booked?",
            "choices": [
                {"emoji": "✈️", "label": "Yes — I have details", "desc": ""},
                {"emoji": "📅", "label": "Not yet — I'll add later", "desc": ""},
                {"emoji": "🤷", "label": "Help me figure it out", "desc": ""},
            ],
            "multi_select": False,
        },
        "INTERESTS": {
            "text": "What types of experiences light you up? Pick everything that excites you!",
            "choices": [
                {"emoji": "🏔️", "label": "Mountains & Hiking", "desc": ""},
                {"emoji": "🌊", "label": "Ocean & Marine", "desc": ""},
                {"emoji": "🍷", "label": "Food & Wine", "desc": ""},
                {"emoji": "📸", "label": "Photography", "desc": ""},
                {"emoji": "🪂", "label": "Adrenaline", "desc": ""},
                {"emoji": "🌿", "label": "Nature & Wildlife", "desc": ""},
                {"emoji": "📖", "label": "Culture & History", "desc": ""},
                {"emoji": "⭐", "label": "Stargazing", "desc": ""},
            ],
            "multi_select": True,
        },
        "MUST_DOS": {
            "text": "Any absolute must-dos? Pick everything that excites you!",
            "choices": [
                {"emoji": "🏔️", "label": "Milford Sound", "desc": ""},
                {"emoji": "🌋", "label": "Tongariro Crossing", "desc": ""},
                {"emoji": "⭐", "label": "Hobbiton", "desc": ""},
                {"emoji": "🧊", "label": "Glacier Hike", "desc": ""},
                {"emoji": "🪂", "label": "Queenstown Bungy", "desc": ""},
                {"emoji": "🐋", "label": "Whale Watching", "desc": ""},
                {"emoji": "🛶", "label": "Abel Tasman", "desc": ""},
                {"emoji": "🌌", "label": "Stargazing", "desc": ""},
            ],
            "multi_select": True,
        },
        "PROVIDERS": {
            "text": "Let's find the perfect bungy experience! Here are the best across New Zealand:",
            "choices": None,
            "provider_cards": [
                {"emoji": "🏆", "name": "AJ Hackett Nevis", "location": "Queenstown", "rating": 4.9, "reviews": 1890, "price": 275, "whatsSpecial": "NZ's HIGHEST at 134m. Suspended over a canyon.", "buddiPick": True},
                {"emoji": "🌊", "name": "Taupo Bungy", "location": "Taupo", "rating": 4.7, "reviews": 1120, "price": 189, "whatsSpecial": "47m over the Waikato River, cliff-face backdrop", "buddiPick": False},
                {"emoji": "🏔️", "name": "AJ Hackett Kawarau", "location": "Queenstown", "rating": 4.8, "reviews": 2340, "price": 205, "whatsSpecial": "The ORIGINAL bungy site. Historic, iconic.", "buddiPick": False},
            ],
        },
        "AUTONOMOUS": {
            "text": "Almost done! I can handle the day-by-day ordering and timing — or would you like to sequence things yourself?",
            "choices": [
                {"emoji": "🤖", "label": "You decide", "desc": "I trust you, Buddi!"},
                {"emoji": "✋", "label": "Let me see options first", "desc": ""},
            ],
            "multi_select": False,
        },
        "GENERATING": {
            "text": "Your trip is ready! 🎉 18 incredible days across New Zealand's South Island. I've optimized for conditions, spread out the highlights, and found the best providers for everything.\n\nHere's a preview of your first few days:\n\n📍 Day 1 — Christchurch: ✈️ Arrive, pick up campervan\n📍 Day 2 — Kaikoura: 🐬 Dolphins · 🐋 Whales · 🦭 Seals\n📍 Day 3 — Hanmer Springs: ♨️ Hot Springs · 🥾 Hiking\n\n...and 15 more incredible days ahead!",
            "choices": None,
            "multi_select": False,
        },
    }
    return fallbacks.get(step, {"text": "Let's continue planning!", "choices": None})
