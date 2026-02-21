# Screen Flows & Wireframe Descriptions

## Overview

This document describes each major screen in the application, its layout, key elements, and interaction behaviors. These serve as specifications for visual design and frontend development.

## Screen Inventory

```
1. Landing Page
2. Auth (Magic Link)
3. Planning Chat
4. Itinerary Overview
5. Day Detail
6. Daily Briefing
7. Activity Detail
8. Swap Suggestion
9. Chat (Free-form)
10. Map View
11. Settings
12. Trip Dashboard
```

---

## 1. Landing Page

### Purpose
Convert visitors into users. Communicate the unique value proposition.

### Layout
```
┌─────────────────────────────────────┐
│ HERO                                │
│ "Your AI Travel Companion"          │
│ [Start Planning — Free]             │
├─────────────────────────────────────┤
│ VALUE PROPS (3 columns)             │
│ [AI Plans]  [Live Adapt]  [Expert]  │
├─────────────────────────────────────┤
│ HOW IT WORKS (3 steps visual)       │
│ 1. Chat → 2. Plan → 3. Travel      │
├─────────────────────────────────────┤
│ EXAMPLE BRIEFING (screenshot/demo)  │
│ Show a real daily briefing example   │
├─────────────────────────────────────┤
│ DESTINATIONS (currently NZ)         │
│ "Starting with New Zealand"         │
├─────────────────────────────────────┤
│ CTA — "Start Your Trip"             │
└─────────────────────────────────────┘
```

### Key Design Notes
- Full-bleed hero image (NZ landscape)
- The example briefing is the killer section — it shows what no one else does
- Clean, modern, premium feel — not cluttered travel-site aesthetic
- Mobile: Stack vertically, hero takes full viewport height

---

## 2. Auth (Magic Link)

### Purpose
Minimal friction account creation/login.

### Flow
```
[Email Input] → [Check Email] → [Click Link] → [Logged In]
```

### Layout
```
┌─────────────────────────────────────┐
│                                     │
│   Journey Buddi logo                │
│                                     │
│   "Enter your email to get started" │
│   [email@example.com           ]    │
│   [Send Magic Link]                 │
│                                     │
│   "No password needed — we'll send  │
│    you a link to sign in"           │
│                                     │
└─────────────────────────────────────┘
```

### States
- **Initial:** Email input with send button
- **Sent:** "Check your email! We sent a link to [email]" with "Resend" option
- **Error:** "Hmm, that didn't work. Try again or use a different email"

---

## 3. Planning Chat

### Purpose
The conversational planning interface where Buddi builds the trip.

### Layout
```
┌─────────────────────────────────────┐
│ HEADER                              │
│ [←] Planning Your NZ Trip    [···]  │
├─────────────────────────────────────┤
│ PROGRESS BAR                        │
│ ●━━●━━●━━○━━○━━○━━○━━○             │
│ Profile  Dest  Interests  ...       │
├─────────────────────────────────────┤
│                                     │
│ CHAT AREA (scrollable)              │
│                                     │
│  ┌─────────────────────────┐       │
│  │ Buddi: "Hey! I'm Buddi, │       │
│  │ your travel companion..."│       │
│  └─────────────────────────┘       │
│                                     │
│  ┌─────────────────────────┐       │
│  │ CHOICE CARD              │       │
│  │ ┌─────┐ ┌─────┐ ┌─────┐│       │
│  │ │ 🌿  │ │ 🥾  │ │ 🧗  ││       │
│  │ │Scenic│ │Activ│ │Thrill││      │
│  │ └─────┘ └─────┘ └─────┘│       │
│  └─────────────────────────┘       │
│                                     │
│  ┌──────────┐                      │
│  │ User: 🥾 │                      │
│  └──────────┘                      │
│                                     │
│  ┌─────────────────────────┐       │
│  │ Buddi: "Great choice!..."│      │
│  └─────────────────────────┘       │
│                                     │
├─────────────────────────────────────┤
│ INPUT AREA (usually hidden during   │
│ structured choices, visible for     │
│ free-form chat)                     │
│ [Type a message...         ] [Send] │
└─────────────────────────────────────┘
```

### Key Elements
- **Progress bar:** Shows which planning step the user is on (subtly, not prominently)
- **Buddi messages:** Left-aligned bubbles with Buddi avatar
- **User messages:** Right-aligned bubbles
- **Choice cards:** Special UI elements embedded in the chat — visual, tappable options
- **Multi-select gallery:** Grid of selectable items with icons
- **Recommendation cards:** Highlighted Buddi suggestion with accept/alternative buttons
- **Text input:** Available but de-emphasized during structured flow; prominent for free-form

### Animations
- Buddi's messages appear with a subtle typing indicator before revealing
- Choice cards slide up from bottom or expand in place
- Selections are confirmed with a brief animation (checkmark, highlight)

---

## 4. Itinerary Overview

### Purpose
Day-by-day view of the complete trip after planning is complete.

### Layout
```
┌─────────────────────────────────────┐
│ HEADER                              │
│ NZ South Island — 18 Days    [Map]  │
├─────────────────────────────────────┤
│                                     │
│ TRIP SUMMARY BAR                    │
│ 18 days • 12 activities • 2,400km  │
│                                     │
├─────────────────────────────────────┤
│                                     │
│ DAY CARDS (scrollable list)         │
│                                     │
│ ┌─────────────────────────────┐    │
│ │ Day 1 — Dec 5                │    │
│ │ 📍 Christchurch              │    │
│ │ Arrive, pick up campervan    │    │
│ │ 🟢 (condition status, when   │    │
│ │     trip is active)          │    │
│ └─────────────────────────────┘    │
│                                     │
│ ┌─────────────────────────────┐    │
│ │ Day 2 — Dec 6                │    │
│ │ 📍 Kaikoura                  │    │
│ │ 🐬 Dolphins • 🐋 Whales      │    │
│ │ 🚗 2.5h drive from ChCh     │    │
│ └─────────────────────────────┘    │
│                                     │
│ ... (more days)                     │
│                                     │
└─────────────────────────────────────┘
```

### Interactions
- Tap any day card to open Day Detail
- During active trip, current day is highlighted and pinned to top
- Condition indicators appear once trip is live
- Pre-trip: cards show planned activities
- Active trip: cards show conditions + activity status

---

## 5. Day Detail

### Purpose
Complete information about one specific day.

### Layout
```
┌─────────────────────────────────────┐
│ HEADER                              │
│ [←] Day 7 — Kaikoura        [Map]  │
├─────────────────────────────────────┤
│                                     │
│ WEATHER BAR                         │
│ ☀️ 18°C  💨 12km/h  🌤 Partly cloud│
│                                     │
├─────────────────────────────────────┤
│                                     │
│ TIMELINE                            │
│ 7:00  Wake up, breakfast            │
│ 8:30  Depart for Whale Watch        │
│ 9:15  🐋 Whale Watching [🟢]       │
│ 12:30 Lunch                         │
│ 2:00  🦭 Seal Colony [🟢]          │
│ 2:45  🚶 Peninsula Walk [🟢]       │
│ 5:00  Free time                     │
│                                     │
├─────────────────────────────────────┤
│                                     │
│ ACTIVITY CARDS (expandable)         │
│ ┌─────────────────────────────┐    │
│ │ 🐋 Whale Watching            │    │
│ │ Conditions: 🟢 Excellent     │    │
│ │ [Expand for full guidance]   │    │
│ └─────────────────────────────┘    │
│                                     │
│ ┌─────────────────────────────┐    │
│ │ 🦭 Seal Colony               │    │
│ │ Conditions: 🟢 Excellent     │    │
│ │ [Expand for full guidance]   │    │
│ └─────────────────────────────┘    │
│                                     │
├─────────────────────────────────────┤
│ 🎒 PACKING LIST                    │
│ ✅ Warm layer  ✅ Sunscreen        │
│ ✅ Camera      ✅ Water bottle     │
├─────────────────────────────────────┤
│ ✨ HIDDEN GEM                      │
│ "Point Kean at dusk — seal pups..."│
└─────────────────────────────────────┘
```

---

## 6. Daily Briefing

### Purpose
The morning notification content — the primary daily touchpoint.

### Layout
Same as Day Detail but entered from the notification, with emphasis on today's condition assessment and the overall "go/adjust" recommendation at the top.

---

## 7. Swap Suggestion

### Purpose
Present a proposed itinerary change clearly.

### Layout
```
┌─────────────────────────────────────┐
│ HEADER                              │
│ Itinerary Suggestion 🔄             │
├─────────────────────────────────────┤
│                                     │
│ ⚠️ ISSUE                            │
│ "Tomorrow's Tongariro Crossing      │
│  conditions are poor: 65km/h wind,  │
│  low cloud cover, rain showers"     │
│                                     │
├─────────────────────────────────────┤
│                                     │
│ PROPOSED CHANGE                     │
│                                     │
│ ┌───────┐    ┌───────┐            │
│ │Day 7  │ ⇄  │Day 9  │            │
│ │BEFORE │    │BEFORE │            │
│ │Tonga- │    │Taupō  │            │
│ │riro   │    │Lake   │            │
│ │🔴     │    │🟡     │            │
│ │       │    │       │            │
│ │AFTER  │    │AFTER  │            │
│ │Taupō  │    │Tonga- │            │
│ │Lake   │    │riro   │            │
│ │🟡     │    │🟢     │            │
│ └───────┘    └───────┘            │
│                                     │
├─────────────────────────────────────┤
│                                     │
│ 💡 WHY THIS WORKS                  │
│ "Saturday has clear skies and       │
│  light winds — perfect for the      │
│  crossing. Tomorrow, Taupō lake     │
│  activities work great in any       │
│  weather."                          │
│                                     │
│ 📋 WHAT CHANGES                    │
│ • Day 7: Huka Falls + Craters      │
│ • Day 8: No change (Rotorua)       │
│ • Day 9: Tongariro Crossing 🟢     │
│ • Extra 45min drive on Day 9       │
│                                     │
├─────────────────────────────────────┤
│                                     │
│ [✅ Accept — Update My Itinerary]   │
│ [❌ Keep Original Plan]             │
│ [💬 Tell Me More]                   │
│                                     │
└─────────────────────────────────────┘
```

### Key Design Notes
- Visual before/after with condition emoji makes the improvement obvious
- Logistics impact is honest and upfront
- Accept is the primary action (bigger, more prominent)
- Decline is easy and judgment-free

---

## 8-12. Additional Screens

Detailed in the design system and implementation specs. Key notes:

**Chat (Free-form):** Standard chat interface, Buddi always has context about the current trip.

**Map View:** Mapbox-based, shows full route with attraction pins, color-coded by condition during active trip.

**Settings:** Notification timing, quiet hours, profile edits, trip management.

**Trip Dashboard:** Hub screen showing current trip status, quick access to today's briefing, upcoming activities, and chat.
