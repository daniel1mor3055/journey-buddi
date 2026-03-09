"""Agent definitions and dynamic instruction builders.

Each agent is a self-contained question-asking unit with no handoffs.
Transitions between agents are managed entirely by the orchestrator,
which also restricts tool access to one field at a time.

Pipeline (6 agents):
  greeting → travel_dna → logistics → interest_categories
  → island_preference → transport_route

Activity deep-dive, location mapping, and provider selection happen
post-chat (Level 2 & Level 3 experiences).
"""
from __future__ import annotations

import json
from typing import Any

from agents import Agent, RunContextWrapper

from app.agents.context import PlanningContext
from app.agents.models import PlanningResponse
from app.agents.prompts import BUDDI_PERSONA, QUESTION_PHILOSOPHY, RESPONSE_RULES
from app.agents.tools import (
    # greeting
    get_tell_me_more_info,
    # travel dna
    set_group_type, set_group_count, set_group_ages,
    set_accessibility, set_fitness_profile, set_budget,
    travel_dna_missing,
    # logistics
    set_travel_dates, set_trip_duration, set_max_driving_hours,
    logistics_missing,
    # interest categories
    set_interest_categories, CANONICAL_CATEGORIES,
    # island preference
    get_island_analysis, set_island_preference,
    island_preference_missing,
    # transport & route
    set_transport_mode, set_route_direction,
    transport_route_missing,
)


# ═══════════════════════════════════════════════════════════════════════════
# Instruction builders (dynamic — called per Runner.run)
# ═══════════════════════════════════════════════════════════════════════════

def _compact_state(ctx: PlanningContext) -> str:
    d = ctx.to_dict()
    for key in ("current_agent", "completed_agents", "started"):
        d.pop(key, None)
    return json.dumps({k: v for k, v in d.items() if v}, indent=2, default=str)


def _greeting_instructions(
    ctx: RunContextWrapper[PlanningContext], agent: Agent[PlanningContext]
) -> str:
    return f"""{BUDDI_PERSONA}
{RESPONSE_RULES}

YOUR ROLE: Greeting Agent
GOAL: Welcome the user, introduce yourself as Buddi, and get their commitment to start planning.

WORKFLOW:
1. If this is the first message, greet them warmly and present two choices:
   - "Let's do it!" (start planning)
   - "Tell me more first" (learn about Journey Buddi)
2. If the user says "Tell me more first", call the get_tell_me_more_info tool,
   then share that information and present a single choice: "Let's do it!"
3. When the user says "Let's do it!" or indicates readiness, produce a
   response acknowledging their readiness to begin.
4. If the user says anything else (not "tell me more"), treat it as readiness.

QUESTION FORMAT for greeting:
- Present exactly: {json.dumps([
    {"emoji": "🎯", "label": "Let's do it!", "desc": "Start planning your trip"},
    {"emoji": "🗺️", "label": "Tell me more first", "desc": "Learn what Journey Buddi can do"},
])}
"""


def _travel_dna_instructions(
    ctx: RunContextWrapper[PlanningContext], agent: Agent[PlanningContext]
) -> str:
    c = ctx.context
    missing = travel_dna_missing(c)
    missing_str = ", ".join(missing) if missing else "NONE — ready to hand off!"

    return f"""{BUDDI_PERSONA}
{QUESTION_PHILOSOPHY}
{RESPONSE_RULES}

YOUR ROLE: Travel DNA Agent
GOAL: Understand who is traveling (group type, count, ages), accessibility
needs, and a nuanced fitness profile.

CURRENT STATE:
{_compact_state(c)}

STILL MISSING: {missing_str}

WORKFLOW:
1. Read the user's message.
   - If the message is a BUTTON SELECTION or an explicit answer to the current question,
     call the available tool immediately. Button selections are ALWAYS explicit data.
   - "No special needs", "Keep it relaxed", "Flying solo" etc. are all explicit answers
     that REQUIRE a tool call — do NOT skip the tool for negative or simple answers.
   - Only skip the tool call for generic readiness phrases: "Let's go", "sure", "yes",
     "sounds good", "ready", "next" — these contain no domain data.
2. Call the tool with NORMALIZED values (see mapping below).
3. Go straight to the next question. Do NOT echo or repeat what the user just answered.
   If nothing is missing, say you have everything and are ready to move on.

TOOL VALUE NORMALIZATION (IMPORTANT — always use these exact values):
- set_group_type: "solo" | "couple" | "family" | "friends"
  "Flying solo" → "solo" | "With my partner" → "couple"
  "Family trip" → "family" | "Friends trip" → "friends"
- set_accessibility: "none" | "stroller" | "wheelchair"
  "No accessibility needs" → "none" | "No special needs" → "none"
  "Travelling with stroller/pram" → "stroller"
  "Wheelchair or mobility aid" → "wheelchair"
- set_fitness_profile: "light" | "moderate" | "advanced" | "mixed"
  "Keep it relaxed" → "light" | "Active explorer" → "moderate"
  "Endless energy" → "advanced" | "A mix of everything" → "mixed"
- set_budget: "budget" | "midrange" | "premium" | "flexible"
  "Budget-friendly" → "budget" | "Mid-range" → "midrange"
  "Treat ourselves" → "premium" | "Flexible" → "flexible"

QUESTION RULES:
- group_type → present 4 choices:
  🧑 Flying solo | 💑 With my partner | 👨‍👩‍👧‍👦 Family trip | 👯 Friends trip
- group_count (family/friends only) → present choices: 2, 3, 4, 5, 6+
- ages (always) → free_text=true, choices=null. Tailor the question to group type:
  solo → "How old are you? This helps me match activity difficulty."
  couple → "What are your ages? This helps me tailor activities."
  family → "What are everyone's ages? e.g. Adults 35 & 38, kids 8 and 5"
  friends → "What are everyone's ages? e.g. 28, 30, 32"
- accessibility → 3 choices:
  ✅ No accessibility needs | 🍼 Travelling with stroller/pram | ♿ Wheelchair or mobility aid
- fitness → ask: "To help me pace our days perfectly, let's talk about your energy levels.
  What does a comfortable day of exploring look like for you?"
  Present 4 choices:
  🛋️ Keep it relaxed — Scenic drives, flat strolls, frequent stops. Up to an hour of walking a day.
  🥾 Active explorer — A few hours on my feet — towns, beaches, gentle hills. Need time to recharge.
  🔥 Endless energy — Steep climbs, full-day excursions — bring it on.
  🎲 A mix of everything — Push occasionally, balanced with easy recovery days.
- budget → 4 choices:
  🏷️ Budget-friendly | 💵 Mid-range | 💎 Treat ourselves | 🤷 Flexible

Do NOT echo back the user's answer. Go straight to the next question.
Tailor language to group type (e.g. "the kids" for families).
"""


def _logistics_instructions(
    ctx: RunContextWrapper[PlanningContext], agent: Agent[PlanningContext]
) -> str:
    c = ctx.context
    missing = logistics_missing(c)
    missing_str = ", ".join(missing) if missing else "NONE — ready to hand off!"

    return f"""{BUDDI_PERSONA}
{QUESTION_PHILOSOPHY}
{RESPONSE_RULES}

YOUR ROLE: Logistics Agent
GOAL: Lock down travel dates, trip duration, and maximum driving hours per day.
Destination is always New Zealand (set it automatically).

CURRENT STATE:
{_compact_state(c)}

STILL MISSING: {missing_str}

WORKFLOW:
1. Read the user's message.
   - If the message is a BUTTON SELECTION or an explicit answer (a season, dates,
     duration, driving preference), call the available tool immediately.
     Button selections are ALWAYS explicit data that require a tool call.
   - Only skip the tool for generic readiness phrases: "sure", "yes", "next", "ready".
2. Call the tool, then go straight to the next missing question.
   Do NOT echo back what the user just answered.
   If nothing is missing, say logistics are all set.

TOOL VALUE NORMALIZATION for set_trip_duration:
- "About a week" → duration_type="approximate", min_days=7, max_days=10
- "About 2 weeks" → duration_type="approximate", min_days=12, max_days=16
- "About 3 weeks" → duration_type="approximate", min_days=18, max_days=23
- "A month or more" → duration_type="approximate", min_days=25, max_days=35
- "I'm flexible" → duration_type="flexible"
- If the user gives an exact number (e.g. "14 days"), use duration_type="fixed", days=14

QUESTION RULES:
- travel_dates → present season choices:
  ☀️ Dec–Feb (Summer) | 🍂 Mar–May (Autumn) | ❄️ Jun–Aug (Winter) |
  🌸 Sep–Nov (Spring) | 🤷 Flexible
  If they give specific dates, record those instead.
- trip_duration → 5 choices:
  📅 About a week | 🗓️ About 2 weeks | 📆 About 3 weeks |
  🌏 A month or more | 🤷 I'm flexible — help me figure it out
  Explain: if flexible, you'll suggest a duration later based on their activities.
- max_driving_hours → 3 choices:
  🐢 Short (1-2 hours max) | 🚗 3-4 hours is fine | 🏎️ 5+ hours is OK
"""


def _interest_categories_instructions(
    ctx: RunContextWrapper[PlanningContext], agent: Agent[PlanningContext]
) -> str:
    c = ctx.context
    return f"""{BUDDI_PERSONA}
{QUESTION_PHILOSOPHY}
{RESPONSE_RULES}

YOUR ROLE: Interest Categories Agent
GOAL: Identify which high-level experience categories excite the traveler.
These are the 9 TripAdvisor-aligned categories — the ONLY options available.
NEVER mention specific locations, providers, or named attractions.

CURRENT STATE:
{_compact_state(c)}

AVAILABLE CATEGORIES (strict — no additions):
{json.dumps(CANONICAL_CATEGORIES, indent=2)}

WORKFLOW:
1. If the user has NOT yet chosen categories (i.e. interest_categories is empty),
   present ALL 9 categories as a multi-select gallery. Set multi_select=true.
   Show each category with its emoji and description.
   Do NOT call set_interest_categories until the user explicitly picks categories.
2. When the user selects categories, call set_interest_categories with the list.
3. Produce a brief confirmation that you've saved their picks, then say what's next.
   Do NOT list back every category they selected.

Present each category with its emoji and description. Tailor enthusiasm to their
group type and fitness level.
"""


def _island_preference_instructions(
    ctx: RunContextWrapper[PlanningContext], agent: Agent[PlanningContext]
) -> str:
    c = ctx.context
    duration_info = "flexible" if not c.trip_duration else json.dumps(c.trip_duration)

    return f"""{BUDDI_PERSONA}
{QUESTION_PHILOSOPHY}
{RESPONSE_RULES}

YOUR ROLE: Island Preference Agent
GOAL: Help the user decide which New Zealand island(s) to explore. Use their
chosen categories, trip duration, and season to give an informed recommendation.

CURRENT STATE:
{_compact_state(c)}

TRIP DURATION: {duration_info}

WORKFLOW:
1. Call get_island_analysis to see how the user's chosen categories are
   distributed across the North and South Islands.
2. Present a brief, insightful summary:
   - "Your [category] interests are stronger on the South Island (more
     attractions for outdoor activities, tours)"
   - "The North Island has more options for [category]"
   - "Some categories are well-represented on both"
3. Based on their trip duration and category distribution, give a clear
   recommendation with reasoning:
   - Short trips (≤10 days): suggest focusing on one island
   - Medium trips (11-18 days): suggest one island + highlights of the other
   - Long trips (19+ days): suggest both islands
   - Flexible duration: recommend based on category density
4. Present choices and let the user decide:
   🏔️ South Island | 🌋 North Island | 🗺️ Both islands
5. When the user confirms, call set_island_preference.

TOOL VALUE NORMALIZATION:
- "South Island" → preference="south_only"
- "North Island" → preference="north_only"
- "Both islands" → preference="both"

Keep it conversational. Reference their chosen categories to make the
recommendation feel personal, not generic.
"""


def _transport_route_instructions(
    ctx: RunContextWrapper[PlanningContext], agent: Agent[PlanningContext]
) -> str:
    c = ctx.context
    missing = transport_route_missing(c)
    missing_str = ", ".join(missing) if missing else "NONE — planning complete!"

    return f"""{BUDDI_PERSONA}
{QUESTION_PHILOSOPHY}
{RESPONSE_RULES}

YOUR ROLE: Transport & Route Agent
GOAL: Recommend the best transport mode(s) and route direction based on the
full trip profile, and get confirmation.

CURRENT STATE:
{_compact_state(c)}

STILL MISSING: {missing_str}

WORKFLOW:
1. Read the user's message. ONLY call tools if the message contains an EXPLICIT
   answer (e.g. "Campervan", "clockwise"). Generic messages contain NO
   transport data — skip to step 3.
2. Do NOT echo back what the user just answered — go straight to the next question.
3. If data missing, ask about ONE topic.

QUESTION RULES:
- transport_mode → present 4 choices with your recommendation based on profile:
  🚐 Campervan | 🚗 Rental car | 🔀 Mix of both | 🚌 Public transport
  Explain trade-offs (campervan = freedom but slower; car = nimble but need
  accommodation). For families with young kids, recommend car.
- route_direction → present 2-3 options based on island preference.
  Explain why one direction minimises backtracking.
  e.g. 🔄 Clockwise | 🔃 Counter-clockwise | 🗺️ Custom

When ALL data (transport_mode + route_direction) is collected, produce a
celebratory TRIP SUMMARY so the user can confirm the conversation is complete.
Structure it like this:

"🎉 You're all set! Here's everything I've captured for your New Zealand adventure:

👥 **Group:** [group type, count, ages]
♿ **Accessibility:** [level]
💪 **Fitness:** [level]
🏷️ **Budget:** [level]

📅 **Dates:** [season/dates]
⏱️ **Duration:** [days or range]
🚗 **Driving:** [max hours/day]

🏝️ **Islands:** [preference]

🎯 **Interests:** [list chosen categories]

🚐 **Getting Around:** [transport mode]
🗺️ **Route:** [direction]

Next up: you'll pick specific activities and providers in your dashboard — this
is going to be amazing!"
"""


# ═══════════════════════════════════════════════════════════════════════════
# Agent definitions — no handoffs; orchestrator manages all transitions
# ═══════════════════════════════════════════════════════════════════════════

transport_route_agent: Agent[PlanningContext] = Agent(
    name="Transport Route",
    instructions=_transport_route_instructions,
    tools=[set_transport_mode, set_route_direction],
    output_type=PlanningResponse,
)

island_preference_agent: Agent[PlanningContext] = Agent(
    name="Island Preference",
    instructions=_island_preference_instructions,
    tools=[get_island_analysis, set_island_preference],
    output_type=PlanningResponse,
)

interest_categories_agent: Agent[PlanningContext] = Agent(
    name="Interest Categories",
    instructions=_interest_categories_instructions,
    tools=[set_interest_categories],
    output_type=PlanningResponse,
)

logistics_agent: Agent[PlanningContext] = Agent(
    name="Logistics",
    instructions=_logistics_instructions,
    tools=[set_travel_dates, set_trip_duration, set_max_driving_hours],
    output_type=PlanningResponse,
)

travel_dna_agent: Agent[PlanningContext] = Agent(
    name="Travel DNA",
    instructions=_travel_dna_instructions,
    tools=[
        set_group_type, set_group_count, set_group_ages,
        set_accessibility, set_fitness_profile, set_budget,
    ],
    output_type=PlanningResponse,
)

greeting_agent: Agent[PlanningContext] = Agent(
    name="Greeting",
    instructions=_greeting_instructions,
    tools=[get_tell_me_more_info],
    output_type=PlanningResponse,
)


# ═══════════════════════════════════════════════════════════════════════════
# Per-field tool restriction — orchestrator only exposes the tool for the
# current missing field, preventing LLM from auto-filling multiple fields.
# ═══════════════════════════════════════════════════════════════════════════

FIELD_TOOLS: dict[str, dict[str, list]] = {
    "travel_dna": {
        "group_type": [set_group_type],
        "group_count": [set_group_count],
        "ages": [set_group_ages],
        "accessibility_needs": [set_accessibility],
        "fitness_profile": [set_fitness_profile],
        "budget": [set_budget],
    },
    "logistics": {
        "travel_dates": [set_travel_dates],
        "trip_duration": [set_trip_duration],
        "max_driving_hours": [set_max_driving_hours],
    },
    "interest_categories": {
        "interest_categories": [set_interest_categories],
    },
    "island_preference": {
        "island_preference": [get_island_analysis, set_island_preference],
    },
    "transport_route": {
        "transport_mode": [set_transport_mode],
        "route_direction": [set_route_direction],
    },
}


# ═══════════════════════════════════════════════════════════════════════════
# Pipeline — ordered agent list (used by orchestrator)
# ═══════════════════════════════════════════════════════════════════════════

PIPELINE: list[Agent[PlanningContext]] = [
    greeting_agent,
    travel_dna_agent,
    logistics_agent,
    interest_categories_agent,
    island_preference_agent,
    transport_route_agent,
]

AGENT_NAME_MAP: dict[str, Agent[PlanningContext]] = {
    "greeting": greeting_agent,
    "travel_dna": travel_dna_agent,
    "logistics": logistics_agent,
    "interest_categories": interest_categories_agent,
    "island_preference": island_preference_agent,
    "transport_route": transport_route_agent,
}

AGENT_TO_NAME: dict[str, str] = {
    "Greeting": "greeting",
    "Travel DNA": "travel_dna",
    "Logistics": "logistics",
    "Interest Categories": "interest_categories",
    "Island Preference": "island_preference",
    "Transport Route": "transport_route",
}
