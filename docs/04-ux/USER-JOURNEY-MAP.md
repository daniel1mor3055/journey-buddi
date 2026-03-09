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

### Phase 3: Category Selection & Wrap-Up
**Duration:** 2-4 minutes
**Emotional state:** Engaged, excited (picking what they love)

| Moment | User Action | Buddi Response | Touchpoint |
|--------|------------|---------------|------------|
| Category gallery shown | Multi-selects from 9 categories | Confirms choices with enthusiasm | Gallery card |
| Island preference | Picks South Island / Both | Buddi analyzes category fit per island | Choice card |
| Transport mode | Picks campervan / car / mix | Acknowledges, notes route implications | Choice card |
| Route direction | Picks clockwise / custom | Wraps up conversation, generates skeleton | Choice card |

**Key design consideration:** This phase is intentionally short. The conversation should feel breezy — the user picks broad categories and logistics, then moves on. The excitement of specific activities comes next in the dashboard.

---

### Phase 4: Activity Selection (Post-Chat Dashboard)
**Duration:** 10-20 minutes
**Emotional state:** Engaged, browsing, building excitement

| Moment | User Action | Buddi Response | Touchpoint |
|--------|------------|---------------|------------|
| Dashboard loads | Sees categories they chose | Activities organized by category | Dashboard |
| Browses activities | Selects specific activities of interest | Activity details and descriptions | Activity cards |
| Builds wishlist | Adds bungy, whale watching, etc. | Wishlist tracker updates | Activity tracker |
| Reviews wishlist | Sees all selected activities | Ready for itinerary building | Wishlist view |

**Key design consideration:** This is where the excitement builds. Each activity should feel concrete and exciting. The UI should make browsing and selecting activities feel like shopping for adventures.

---

### Phase 5: Progressive Itinerary Building
**Duration:** 10-20 minutes
**Emotional state:** Anticipation, seeing the trip come alive

| Moment | User Action | Buddi Response | Touchpoint |
|--------|------------|---------------|------------|
| Skeleton itinerary shown | Reviews route with location slots | Day-by-day skeleton on map | Itinerary view |
| Location focus (e.g. Auckland) | Sees available activities here | Shows which wishlist items fit | Location detail |
| Selects activities for location | Picks activities for this stop | Shows provider options | Provider cards |
| Picks providers | Chooses from recommended providers | Itinerary "fills up" for that location | Itinerary update |
| Moves to next location | Repeats for next stop | Activity tracker updates remaining | Location detail |
| All activities placed | Reviews complete itinerary | Celebration moment! Trip is ready | Itinerary view |

**Key design consideration:** The progressive reveal is the big moment. Watching the itinerary fill up location by location feels satisfying. The activity wishlist tracker should always be visible so the user knows what's remaining.

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
2. **Category selection**: Must feel quick and empowering, not tedious
3. **Activity browsing (dashboard)**: Must feel like shopping for adventures, not filling out a form
4. **Progressive itinerary building**: Must feel satisfying — watching the trip come alive
5. **First morning briefing**: Must prove the value of the live companion
6. **First swap suggestion**: Must feel helpful, not disruptive
