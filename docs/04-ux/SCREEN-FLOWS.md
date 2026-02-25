# Screen Flows & Wireframe Descriptions

## Overview

This document describes each major screen in the application, its layout, key elements, and interaction behaviors. These serve as specifications for visual design and frontend development.

### Design Language: Nature-Inspired

Journey Buddi's visual design draws from nature — the destinations we help travelers explore. The interface should feel organic, inviting, and calming:

- **Color palette**: Earth tones, ocean blues, forest greens, warm sunset accents. No harsh neon or corporate blues.
- **Typography**: Clean, readable, with a sense of warmth. Not cold/technical.
- **Iconography**: Organic, hand-drawn-style icons where appropriate. Nature-themed visual elements.
- **Spacing**: Generous whitespace — the app should breathe, like being outdoors.
- **Imagery**: Rich destination photography as backgrounds and accents. Every screen should evoke the feeling of being on an adventure.
- **Interactions**: Smooth, natural animations — elements slide, fade, and breathe rather than snap or flash.
- **Navigation**: Intuitive and effortless. The user should never feel lost in the app — only lost in the beauty of their trip planning.

The goal: opening Journey Buddi should feel like opening a window to the destination.

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

## 4. Itinerary Dashboard (Interactive Control Panel)

### Purpose
The trip command center. Not a static list — a living, interactive dashboard where every element is actionable. This is where the user manages their entire trip.

### Layout
```
┌─────────────────────────────────────────────┐
│ HEADER                                      │
│ NZ South Island — 18 Days            [Map]  │
├─────────────────────────────────────────────┤
│                                             │
│ TRIP SUMMARY BAR                            │
│ 18 days • 12 activities • 2,400km          │
│ ✅ 6 booked • ⚠️ 4 need booking • 2 flex   │
│                                             │
│ [💡 Buddi's Tips]  [🗺️ Treasure Map]       │
│                                             │
├─────────────────────────────────────────────┤
│                                             │
│ DAY CARDS (scrollable, draggable)           │
│                                             │
│ ┌─────────────────────────────────────┐    │
│ │ Day 1 — Dec 5 • Christchurch       │    │
│ │ ✈️ Arrive 2:30 PM (NZ123)          │    │
│ │ 📍 Pick up campervan, explore city  │    │
│ │ 🏨 Christchurch Top 10 ✅ Booked   │    │
│ │ 🟢 92/100  │  📊 Relaxed           │    │
│ └─────────────────────────────────────┘    │
│                                             │
│ ┌─────────────────────────────────────┐    │
│ │ Day 2 — Dec 6 • Kaikoura           │    │
│ │ 🐬 Dolphins ✅ • 🐋 Whales ⚠️      │    │
│ │ 🚗 2.5h drive from ChCh            │    │
│ │ 🏕️ Kaikoura Top 10 ✅ Booked       │    │
│ │ 🟢 88/100  │  📊 Comfortable       │    │
│ └─────────────────────────────────────┘    │
│                                             │
│ ┌─────────────────────────────────────┐    │
│ │ Day 7 — Dec 11 • Abel Tasman       │    │
│ │ 🛶 Kayaking ⚠️ • 🥾 Coast Track ✅ │    │
│ │ 🚗 45min from Nelson               │    │
│ │ 🏨 Not yet booked                  │    │
│ │ 🟠 54/100  │  📊 Tight             │    │
│ │ [🔄 Conditions alert — tap for     │    │
│ │  alternative plan]                  │    │
│ └─────────────────────────────────────┘    │
│                                             │
│ ... (more days)                             │
│                                             │
│ [+ Add a Day]                               │
│                                             │
├─────────────────────────────────────────────┤
│ FLOATING ACTION BUTTON                      │
│ [+ Add Activity]                            │
└─────────────────────────────────────────────┘
```

### Day Card Elements
Each day card displays at a glance:
- **Date and location**
- **Activity icons with booking status** (✅ booked, ⚠️ needs booking)
- **Transport summary** (mode, duration)
- **Accommodation** (type, name, booking status)
- **Condition banner** (score + emoji, confidence indicator)
- **Tightness indicator** (relaxed / comfortable / tight / overpacked)
- **Alert ribbon** (if conditions suggest a change, appears at bottom of card)

### Interactions
- **Tap** any day card → opens Day Detail view
- **Long-press + drag** → reorder days (Buddi validates feasibility)
- **Swipe left** → quick actions (remove day, mark as flex, duplicate)
- **Tap booking status icon** → opens booking flow or shows booking details
- **Tap condition banner** → expands to show detailed forecast
- **Tap "+" button** → add activity flow with Buddi suggesting optimal placement
- **Tap "Buddi's Tips"** → persistent trip-wide tips (discounts, apps, logistics)
- **Tap "Treasure Map"** → hidden gems downloadable to Google Maps

### Active Trip Enhancements
During an active trip:
- Current day is highlighted with a glowing border and pinned to top
- Past days are dimmed but accessible (with completed status)
- Condition indicators update in real-time
- "Today's Briefing" banner appears above the current day
- Upcoming days show forecast confidence indicators

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

### Enhanced Day Detail Elements

The Day Detail view includes all original elements PLUS:

**Condition Banner (top of page):**
```
┌─────────────────────────────────────┐
│ 🟢 GREAT CONDITIONS    Score: 88   │
│ Perfect day for dolphins & walks    │
│ Confidence: High ✓                  │
└─────────────────────────────────────┘
```

**Tightness Indicator:**
```
📊 Day Fill: 67% — Comfortable
   [━━━━━━━━━━━━━░░░░░░░] 
   Plenty of room for spontaneous stops
```

**Activity Cards (enhanced):**
```
┌─────────────────────────────────────┐
│ 🐋 Whale Watching                   │
│ Whale Watch Kaikoura                │
│ ⭐ 4.8 (2,340 reviews)             │
│ ⏰ 9:15 AM - 12:15 PM              │
│ 💰 $155 NZD                        │
│ Conditions: 🟢 Excellent            │
│ Status: ✅ Booked (Ref: WW-8821)   │
│                                     │
│ [📍 Maps] [📋 Details] [✏️ Edit]   │
└─────────────────────────────────────┘
```

**Accommodation Card:**
```
┌─────────────────────────────────────┐
│ 🏕️ Kaikoura Top 10 Holiday Park    │
│ 📍 34 Beach Road, Kaikoura         │
│ Check-in: 2:00 PM | Out: 10:00 AM  │
│ Status: ✅ Booked (Ref: KTP-2847)  │
│ 💰 $55/night                       │
│                                     │
│ [📍 Maps] [📞 Call] [✏️ Change]    │
└─────────────────────────────────────┘
```

**Story Card:**
```
┌─────────────────────────────────────┐
│ 📖 STORY: The Whales of Kaikoura   │
│                                     │
│ "The Kaikoura Canyon plunges to     │
│  1,600m just 1km offshore..."       │
│                                     │
│ [🎧 Listen while walking]          │
│ [📖 Read full story]               │
└─────────────────────────────────────┘
```

**Transport Card:**
```
┌─────────────────────────────────────┐
│ 🚗 Drive: Christchurch → Kaikoura  │
│ 📏 181 km • ⏱️ 2.5 hours           │
│ 🛣️ SH1 — scenic coastal route     │
│                                     │
│ Scenic stops along the way:        │
│ • Waipara wine country (30min)     │
│ • Ohau Point seal colony (15min)   │
│                                     │
│ [📍 Open in Google Maps]           │
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

---

## 13. Treasure Map

### Purpose
A bonus screen showing hidden gems near the user's route that aren't in the itinerary — the "extras" that Buddi knows about from local knowledge.

### Layout
```
┌─────────────────────────────────────┐
│ HEADER                              │
│ 🗺️ Your Treasure Map        [Map]  │
├─────────────────────────────────────┤
│                                     │
│ "These hidden gems are near your    │
│  route but not in your itinerary.   │
│  If you have spare time or pass     │
│  by — they're gold."               │
│                                     │
│ ┌─────────────────────────────┐    │
│ │ 🌊 Secret Waterfall         │    │
│ │ 📍 5 min from Day 7 route   │    │
│ │ "A 100m waterfall hidden..." │    │
│ │ [📍 Save to Google Maps]    │    │
│ └─────────────────────────────┘    │
│                                     │
│ ┌─────────────────────────────┐    │
│ │ ☕ Local's Favorite Café     │    │
│ │ 📍 In Kaikoura town center  │    │
│ │ "The best flat white on the..│    │
│ │ [📍 Save to Google Maps]    │    │
│ └─────────────────────────────┘    │
│                                     │
│ ... (more gems)                     │
│                                     │
├─────────────────────────────────────┤
│ [📥 Download All to Google Maps]    │
│ [🗺️ View on Map]                   │
└─────────────────────────────────────┘
```

### Key Design Notes
- Presented as a "gift" from Buddi at the end of planning
- Each gem can be individually saved to Google Maps
- "Download All" creates a Google Maps custom layer with all gems
- During the trip, gems near the current location get highlighted
- Gems are tagged by type (viewpoint, beach, café, waterfall, wildlife, photo spot)

---

## 14. Audio Stories & Storytelling

### Purpose
Immersive story delivery for attractions, locations, and drives.

### Layout
```
┌─────────────────────────────────────┐
│ HEADER                              │
│ [←] 📖 Stories            [🎧|📖]  │
├─────────────────────────────────────┤
│                                     │
│ NOW PLAYING                         │
│ 🎧 "The Whales of Kaikoura"       │
│                                     │
│ ━━━━━━━━━━●━━━━━━━━━━              │
│ 2:14 / 4:30                        │
│        [⏮️]  [⏸️]  [⏭️]           │
│                                     │
├─────────────────────────────────────┤
│                                     │
│ UP NEXT (based on today's plan):   │
│                                     │
│ ┌─────────────────────────────┐    │
│ │ 🌋 "Fire and Ice" (geology) │    │
│ │ 4:30 • Best while driving   │    │
│ └─────────────────────────────┘    │
│                                     │
│ ┌─────────────────────────────┐    │
│ │ 🦎 "Tuatara: Living Fossil" │    │
│ │ 3:15 • Best at location    │    │
│ └─────────────────────────────┘    │
│                                     │
│ EVENING READS:                     │
│ ┌─────────────────────────────┐    │
│ │ 📖 "Piopiotahi: Milford's   │    │
│ │    Māori Name" (legend)     │    │
│ │ 6 min read                  │    │
│ └─────────────────────────────┘    │
│                                     │
└─────────────────────────────────────┘
```

### Key Design Notes
- Audio player is minimal and unobtrusive — can play in background while Maps is open
- Stories are queued based on the day's itinerary and current activity
- Toggle between audio (🎧) and text (📖) modes
- Evening reading section available in the day detail view
- Stories use Buddi's warm, knowledgeable persona for narration
