# User Journey Map

## End-to-End Journey

This document maps the complete user journey from discovery to post-trip, including emotional states, actions, touchpoints, and opportunities.

## Journey Phases

---

### Phase 0: Discovery
**Duration:** Seconds to minutes
**Emotional state:** Curious, evaluating

| Moment | User Action | Buddi Response | Touchpoint |
|--------|------------|---------------|------------|
| Hears about Journey Buddi | Visits website/app | Clean landing page with value prop | Landing page |
| Scans the page | Reads "Your AI Travel Companion" | Shows example daily briefing screenshot | Hero section |
| Wants to try it | Taps "Start Planning" | Asks for email (magic link) | Auth flow |
| Receives magic link | Taps link in email | Logs in, lands in planning | Email → App |

**Key design consideration:** The landing page must communicate "this is NOT another trip planner" within 5 seconds. Show the LIVE COMPANION aspect — the daily briefing, the swap suggestion, the condition awareness. That's the differentiator.

---

### Phase 1: Onboarding & Profile Building
**Duration:** 2-3 minutes
**Emotional state:** Interested, slightly impatient (wants to get to the good stuff)

| Moment | User Action | Buddi Response | Touchpoint |
|--------|------------|---------------|------------|
| First interaction | Sees Buddi's greeting | "Hey! I'm Buddi..." introduction | Chat screen |
| Adventure preference | Taps one of 3 options | "Great! A [moderate] adventurer..." | Choice card |
| Pace preference | Taps pace option | Acknowledges, moves forward | Choice card |
| Fitness level | Taps fitness option | Notes it naturally | Choice card |
| Budget indication | Taps budget range | "Got it! Let's see what's out there..." | Choice card |
| Interest selection | Multi-selects interests | "Love your choices! Let's dive in..." | Gallery card |

**Key design consideration:** This must feel fast and fun, not like a medical questionnaire. Visual cards with icons, immediate feedback, sense of progress.

---

### Phase 2: Destination & Trip Setup
**Duration:** 1-2 minutes
**Emotional state:** Excited (talking about their trip!)

| Moment | User Action | Buddi Response | Touchpoint |
|--------|------------|---------------|------------|
| Destination choice | Selects NZ | "Amazing choice! NZ is perfect for what you love..." | Choice card |
| Date selection | Picks dates | Notes seasonal context | Calendar |
| Region selection | Chooses South Island / Both | "The South Island is incredible — let's build this!" | Choice card |
| Entry/exit airports | Selects airports | Route implications noted | Choice card |

---

### Phase 3: Interest Deep Dive
**Duration:** 10-20 minutes
**Emotional state:** Engaged, excited (seeing concrete possibilities)

| Moment | User Action | Buddi Response | Touchpoint |
|--------|------------|---------------|------------|
| Wildlife options shown | Selects dolphins, penguins, glowworms | Explains locations, makes recommendation | Gallery + recommendation |
| Location advice | Chooses Kaikoura for dolphins | "Perfect choice! I'll pair it with whale watching..." | Chat |
| Mountains & glaciers | Selects glacier, Mt Cook | Recommends Fox over Franz Josef | Recommendation card |
| Hiking selection | Picks Tongariro, Hooker Valley | Notes difficulty, confirms fitness match | Chat |
| Repeat for each interest category... | Selects from curated options | Smart grouping and route awareness | Mixed |

**Key design consideration:** This is the most engaging part of the conversation. Each attraction should feel exciting. Buddi's enthusiasm here is important — "Oh you're going to love this one."

---

### Phase 4: Route & Transport
**Duration:** 3-5 minutes
**Emotional state:** Collaborative, trusting Buddi's expertise

| Moment | User Action | Buddi Response | Touchpoint |
|--------|------------|---------------|------------|
| Route presentation | Reviews suggested route on map | Explains the logic, direction choice | Map + chat |
| Route approval/adjust | Approves or requests changes | Adapts or explains trade-offs | Map + chat |
| Transport suggestion | Reviews campervan vs car rec | Detailed reasoning with cost comparison | Recommendation card |
| Transport decision | Accepts or chooses alternative | Adapts plan accordingly | Choice card |
| Duration suggestion | Reviews "18 days" recommendation | Explains the math, offers trim options | Chat |

---

### Phase 5: Itinerary Review
**Duration:** 5-15 minutes
**Emotional state:** Anticipation, scrutiny (checking the details)

| Moment | User Action | Buddi Response | Touchpoint |
|--------|------------|---------------|------------|
| Full itinerary revealed | Scrolls through day-by-day | Each day has title, activities, transport | Itinerary view |
| Taps a day | Opens day detail | Activities, timing, area info | Day detail |
| Wants to change something | Drags/removes an activity | Re-optimizes affected days | Itinerary view |
| Adds an attraction | Requests new activity | Suggests where it fits, adjusts plan | Chat + itinerary |
| Satisfied | Taps "Confirm Itinerary" | Celebration moment! Trip is ready | Confirmation |

**Key design consideration:** The itinerary reveal is a big moment. It should feel impressive — "Buddi built my entire trip." Consider animation, map fly-through, day counter.

---

### Phase 6: Pre-Departure
**Duration:** Days before trip
**Emotional state:** Anticipation, last-minute prep anxiety

| Moment | User Action | Buddi Response | Touchpoint |
|--------|------------|---------------|------------|
| T-3 days | Opens app | Pre-departure checklist, first days preview | Dashboard |
| Packing | Reviews overall packing list | Aggregated from all activities | Packing view |
| T-1 day | Receives notification | "Tomorrow's the day! Here's your arrival plan..." | Push + briefing |

---

### Phase 7: Active Trip
**Duration:** Entire trip (10-21+ days)
**Emotional state:** Varies daily (excited, tired, amazed, frustrated by weather)

#### Daily Rhythm:

| Time | User Action | Buddi Response | Touchpoint |
|------|------------|---------------|------------|
| Evening before | Receives preview | Tomorrow's plan + packing reminder | Push notification |
| Morning | Reads daily briefing | Full condition report, timing, packing, tips | Briefing screen |
| Pre-activity | Reviews activity detail | Pro tips, viewpoints, logistics | Activity card |
| During activity | Checks a tip | On-demand reference | Activity card |
| Post-activity | Nothing required | Buddi is quiet unless needed | — |
| Evening | Receives tomorrow preview | Next day's preview | Push notification |

#### Swap Events:

| Moment | User Action | Buddi Response | Touchpoint |
|--------|------------|---------------|------------|
| Weather changes | Receives alert | Swap suggestion with reasoning | Push + swap screen |
| Reviews swap | Reads before/after comparison | Clear logistics explanation | Swap detail |
| Accepts swap | Taps "Accept" | Itinerary updated, new briefing generated | Itinerary update |
| OR Declines | Taps "Keep original" | Tips for making the best of current conditions | Chat |

---

### Phase 8: Post-Trip (Future Feature)
**Duration:** Days after trip
**Emotional state:** Nostalgic, satisfied, evaluative

| Moment | User Action | Buddi Response | Touchpoint |
|--------|------------|---------------|------------|
| Trip ends | Opens app | "What an incredible trip! Here's your journey recap" | Recap screen |
| Reviews trip | Scrolls through highlights | Stats, favorite moments, conditions faced | Trip summary |
| Provides feedback | Rates tips and suggestions | "Thanks! This helps me get even better" | Feedback form |
| Considers next trip | Browses destinations | "When you're ready for the next one, I'm here" | Home screen |

## Journey Metrics

For each phase, track:
- **Completion rate**: What % of users complete this phase?
- **Time spent**: How long does this phase take?
- **Drop-off points**: Where do users abandon?
- **Satisfaction signals**: Positive/negative interactions?
- **Feature engagement**: Which features are used vs. ignored?

## Critical Moments (Make or Break)

1. **First Buddi interaction**: Must feel magical, not robotic
2. **Interest deep dive**: Must feel exciting, not tedious
3. **Itinerary reveal**: Must feel impressive and trustworthy
4. **First morning briefing**: Must prove the value of the live companion
5. **First swap suggestion**: Must feel helpful, not disruptive
