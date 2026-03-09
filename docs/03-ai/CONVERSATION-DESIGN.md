# AI Conversation Design

## Overview

Every AI-driven conversation in Journey Buddi follows a common design philosophy: structured choices, progressive depth, and contextual intelligence. This document defines the patterns, anti-patterns, and technical design of human-AI conversations across the product.

## Conversation Patterns

### Pattern 1: Structured Choice

The foundational pattern. Present options, user selects.

```
Buddi: [Context/framing text]
       [Option A with description]
       [Option B with description]  
       [Option C with description]
       [Optional: "Tell me more" or "None of these"]
```

**When to use:** Whenever the user needs to make a decision.

**Key rules:**
- 3-5 options maximum per question (avoid choice overload)
- Each option has a brief description, not just a label
- Include an escape hatch ("none of these" or "tell me more")
- Buddi may indicate a recommendation: "I'd go with Option B — here's why"

### Pattern 2: Multi-Select Gallery

For interest/activity selection where multiple items can be chosen.

```
Buddi: [Context/framing text]
       [Item 1 with icon + brief description]
       [Item 2 with icon + brief description]
       ...
       [Item N with icon + brief description]
       [Select all that interest you]
```

**When to use:** Interest mapping, activity selection, feature preferences.

**Key rules:**
- Visual icons for scannability
- Clear "select all that interest you" instruction
- Brief descriptions (1 line each)
- "Select all" and "Select none" shortcuts if >6 items
- Group into categories if >10 items

### Pattern 3: Recommendation with Override

Buddi provides a clear recommendation but the user can choose differently.

```
Buddi: [Recommendation with reasoning]
       [Why this is the best option]
       [What the alternative would mean]
       
       [Accept recommendation]
       [Choose alternative]
       [Tell me more]
```

**When to use:** Transport mode selection, attraction location choices, duration decisions.

**Key rules:**
- Lead with the recommendation (don't bury it in options)
- Explain the reasoning (users trust recommendations they understand)
- Make the alternative easy to choose (no judgment)
- If overridden, gracefully adapt ("Great choice! Here's how we'll make that work...")

### Pattern 4: Confirmation Summary

After a significant decision, summarize what was decided.

```
Buddi: [Summary of decisions made so far]
       [Any implications or notes]
       
       [Looks good, continue!]
       [I want to change something]
```

**When to use:** After completing a section of planning, before moving to the next phase.

**Key rules:**
- Concise but complete summary
- Highlight any interdependencies ("since you chose X, I've adjusted Y")
- Easy to go back and change
- Provides sense of progress

### Pattern 5: Progressive Disclosure

Start with the essential question, offer depth on request.

```
Buddi: [Brief version of the information/question]
       
       [Quick answer option]
       [Tell me more about this]
```

**When to use:** When detailed information is available but might overwhelm.

**Key rules:**
- Default to brevity
- "Tell me more" always available
- Detail expands in-place (doesn't open a new screen)
- Users who want depth can get it; users who don't aren't burdened

### Pattern 6: Free Text with Guardrails

Occasionally, free text is needed. But always with context and suggestions.

```
Buddi: [Question with context]
       [Suggestion/example to guide the response]
       
       [Free text input]
       [Or choose from common answers: A, B, C]
```

**When to use:** Edge cases where structured choices can't cover all possibilities (e.g., "Is there anything specific you want to do that I haven't mentioned?")

**Key rules:**
- Always provide examples or suggestions alongside free text
- Parse free text with AI to extract structured intent
- Confirm understanding: "So you'd like to add a wine tasting day in Marlborough — is that right?"

## Conversation State Machine

### States

The conversation has been streamlined into 6 agent steps.  Activity deep-dive,
provider selection, and itinerary building happen post-chat (Levels 2 & 3).

```
GREETING → TRAVEL_DNA → LOGISTICS → INTEREST_CATEGORIES
  → ISLAND_PREFERENCE → TRANSPORT_ROUTE → COMPLETE
```

### State Transitions

Each state transition is triggered by user completion of the current step:

```python
state_machine = {
    "GREETING": {
        "next": "TRAVEL_DNA",
        "required_data": [],
        "can_skip": False
    },
    "TRAVEL_DNA": {
        "next": "LOGISTICS",
        "required_data": ["group_type", "accessibility_needs", "fitness_profile", "budget"],
        "can_skip": False
    },
    "LOGISTICS": {
        "next": "INTEREST_CATEGORIES",
        "required_data": ["travel_dates", "trip_duration", "max_driving_hours"],
        "can_skip": False
    },
    "INTEREST_CATEGORIES": {
        "next": "ISLAND_PREFERENCE",
        "required_data": ["interest_categories"],  # 9 TripAdvisor-aligned categories
        "can_skip": False
    },
    "ISLAND_PREFERENCE": {
        "next": "TRANSPORT_ROUTE",
        "required_data": ["island_preference"],
        "can_skip": False
    },
    "TRANSPORT_ROUTE": {
        "next": "COMPLETE",
        "required_data": ["transport_mode", "route_direction"],
        "can_skip": True  # Buddi can auto-recommend
    },
}
```

### Post-Chat Stages (not in the conversation)

After the conversation completes, the user proceeds through:
- **Level 2 — Activity Selection**: Browse and pick specific activities in the dashboard
- **Level 3 — Provider Selection**: Choose providers inside the progressive itinerary builder

### Back-Navigation

Users can go back to any previous state:
- "I want to change my interests" → Jump back to INTERESTS
- Changes cascade forward (if interests change, attractions need re-evaluation)
- Previously selected items are preserved as defaults when returning to a state

### Conversation Persistence

- Full conversation state is persisted to the database after each turn
- Users can close the app and resume exactly where they left off
- Stale conversations (>30 days inactive) prompt a soft "welcome back" with summary

## Turn Management

### AI Turn Structure

Each AI turn follows:
1. **Acknowledge** — React to the user's previous input (brief)
2. **Process** — Share any relevant insight or decision (medium)
3. **Advance** — Present the next question or action (primary)

```
"Great choices! [ACKNOWLEDGE] Dolphins and whales in Kaikoura will be 
a highlight — the encounter rates there are incredible. [PROCESS] 

Now let's talk about mountains and glaciers. Here are your options 
on the South Island... [ADVANCE]"
```

### Response Length Guidelines

| Context | Target Length | Reasoning |
|---------|-------------|-----------|
| Choice presentation | 3-8 lines + options | Quick scan, choose, move on |
| Recommendation with reasoning | 5-15 lines | Enough to convince, not overwhelm |
| Itinerary summary | 15-30 lines | Comprehensive but scannable |
| Daily briefing | 20-40 lines | The one time we go long — it's the main content |
| Error/change response | 3-5 lines | Quick acknowledgment and action |

### Handling Ambiguity

When the user's input is ambiguous:
1. Don't guess — ask a clarifying question
2. Frame clarification as options, not open-ended
3. "Did you mean [A] or [B]?"
4. Never proceed with an assumption that could lead to wrong planning

### Handling Out-of-Scope

When the user asks about something outside Buddi's domain:
1. Acknowledge the question
2. Redirect to appropriate resources
3. Return to the current planning step

```
User: "Do I need a visa for New Zealand?"
Buddi: "Good question! Visa requirements depend on your nationality. 
       Check the official NZ immigration site (immigration.govt.nz) 
       for the latest requirements. Now, back to your trip — let's 
       talk about those glaciers!"
```

## Error Handling

### AI Response Failures
- If the LLM fails to generate a response, show: "Give me a moment — let me think about this again."
- Retry with the same prompt up to 2 times
- If still failing, show: "I'm having trouble with this one. Let me skip ahead and come back to it."

### Nonsensical User Input
- "Asdfghjkl" → "I didn't quite catch that — could you try again?"
- Repeated nonsense → Show the current state options again
- Never mock or criticize user input

### Long Response Times
- Stream the AI response to the UI (show text appearing in real time)
- Show a subtle "Buddi is thinking..." indicator
- If >15 seconds, show: "This one needs a bit more thought — hang tight..."
