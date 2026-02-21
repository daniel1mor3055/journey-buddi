# User Experience Overview

## UX Philosophy

Journey Buddi's user experience is built on one core belief: **the best technology disappears**. The user shouldn't feel like they're operating a complex tool — they should feel like they're talking to a knowledgeable friend who happens to have perfect memory and access to real-time data.

Every screen, every interaction, every notification should feel natural, helpful, and unobtrusive.

## UX Principles

### 1. Conversation First, Interface Second
The primary interaction model is conversational. Users talk to Buddi, not fill out forms. The UI supports and enhances the conversation, it doesn't replace it.

### 2. Progressive Complexity
Start simple, add detail on demand. The morning briefing is 3 lines of summary that expand into full detail. The itinerary is a clean daily view that opens into activity cards with tips and logistics.

### 3. Glanceable, Then Deep
Every screen has two layers:
- **Glance layer**: What do I need to know in 3 seconds? (condition emoji, one-line summary, departure time)
- **Deep layer**: Tell me everything (full condition report, packing list, pro tips, stories)

### 4. Mobile-Optimized, Desktop-Rich
The primary usage context during trips is mobile (phone). During planning, it's likely desktop or tablet. Design mobile-first but make desktop planning a rich, spatial experience.

### 5. Calm Design
No alarm bells, no aggressive push for engagement, no gamification. This is a companion for a once-in-a-lifetime trip — the design should feel premium, calm, and trustworthy.

## Key Screens

### 1. Landing / Onboarding
**Purpose:** First impression, account creation, start planning.
**Key elements:** Clean hero with destination imagery, one-tap "Start Planning", magic link auth.

### 2. Planning Chat
**Purpose:** The conversational planning experience with Buddi.
**Key elements:** Chat interface with structured choice cards, Buddi's avatar, progress indicator showing planning steps.

### 3. Itinerary View
**Purpose:** Day-by-day overview of the complete trip.
**Key elements:** Timeline/calendar view, activity cards, map integration, condition indicators (once live).

### 4. Day Detail
**Purpose:** Everything about one specific day.
**Key elements:** Detailed activity cards, timeline, packing list, condition report, tips, map of the day's locations.

### 5. Daily Briefing
**Purpose:** Morning summary — the core daily touchpoint.
**Key elements:** Overall assessment, activity breakdown with conditions, timing guidance, packing list, hidden gem.

### 6. Activity Detail
**Purpose:** Deep dive into a specific activity.
**Key elements:** Full guidance (preparation, timing, tips, stories, safety), conditions, photos, map.

### 7. Swap Suggestion
**Purpose:** Present a proposed itinerary change with reasoning.
**Key elements:** Clear before/after comparison, reasoning, logistics impact, accept/decline actions.

### 8. Chat with Buddi
**Purpose:** On-demand conversational access during the trip.
**Key elements:** Chat interface, context-aware (Buddi knows where you are and what's planned).

### 9. Map View
**Purpose:** Spatial overview of the trip.
**Key elements:** Full route on map, attraction pins with condition colors, current location, day-by-day route segments.

### 10. Settings / Profile
**Purpose:** Account, preferences, notification settings.
**Key elements:** Profile info, notification timing, quiet hours, trip management.

## Information Hierarchy

```
Level 1 (Always visible):  Day title, condition emoji, key time
Level 2 (One tap):         Activity list, weather summary, packing preview  
Level 3 (Expand/scroll):   Full guidance, pro tips, stories, detailed conditions
Level 4 (On demand):       Raw data, extended forecast, map details
```

## Interaction Patterns

### The Chat Pattern
For planning and on-demand questions. Buddi speaks in chat bubbles with structured choice cards that the user taps to respond. Text input available but discouraged during planning (Buddi drives the structured flow).

### The Card Pattern
For itinerary viewing and daily briefings. Information is organized into cards that can be collapsed (summary) or expanded (detail). Each card represents one activity, one logistics block, or one information section.

### The Notification Pattern
For proactive communication. Push notifications lead directly to the relevant content in-app. Notifications are self-contained enough to be useful without opening the app, but link to details.

### The Map Pattern
For spatial awareness. The map is available as an overlay or dedicated view. It shows route, attractions, and current location. Map pins indicate condition status (green/yellow/red).

## Emotional Design

### Pre-Trip (Planning Phase)
**Feeling to evoke:** Excitement, anticipation, confidence
**Design approach:** Rich destination imagery, progress indicators (your trip is coming together!), celebratory moments when the itinerary is finalized

### Day Before Departure
**Feeling to evoke:** Preparedness, calm excitement
**Design approach:** Clear checklist, reassuring "you're all set" messaging, countdown

### During Trip — Good Days
**Feeling to evoke:** Joy, confidence, discovery
**Design approach:** Bright, positive condition indicators, enthusiastic tips, celebration of good conditions

### During Trip — Challenging Days
**Feeling to evoke:** Calm, trust, adaptability
**Design approach:** Clear communication, solution-focused swap suggestions, positive framing of alternatives ("rain creates hundreds of temporary waterfalls in Milford Sound")

### Post-Trip
**Feeling to evoke:** Nostalgia, satisfaction, desire to share
**Design approach:** Trip summary with highlights, memories collection, easy sharing
