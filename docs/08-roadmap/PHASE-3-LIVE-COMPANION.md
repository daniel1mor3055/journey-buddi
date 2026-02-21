# Phase 3: Live Companion — Weeks 9-14

## Goal

Build the live companion experience that activates during the trip. Weather and condition monitoring, daily briefings, adaptive itinerary management, and activity guidance. This is where Journey Buddi delivers its unique, differentiated value.

## Week 9: Weather & Condition Integration

### Tasks

**Day 1-2: Weather API Integration**
- Implement weather data fetcher:
  - OpenWeatherMap One Call API 3.0 (or Open-Meteo as free alternative)
  - Fetch hourly + daily forecasts for a location
  - Parse and normalize response to internal format
  - Error handling and fallback
- Build weather data caching layer:
  - Cache to Redis with TTLs (30 min for current, 1 hour for today, 6 hours for multi-day)
  - Stale-while-revalidate pattern
- Write weather normalization schema (Pydantic models)

**Day 3-4: Additional Data Sources**
- Implement tide data integration:
  - WorldTides API or NIWA for NZ
  - High/low tide times and heights
  - Cache daily (tides are highly predictable)
- Implement solar data:
  - Sunrise/sunset times (sunrise-sunset.org API or calculate locally)
  - Golden hour calculations
  - UV index from weather API
- Implement aurora/Kp index (NOAA SWPC API):
  - Only relevant for southern NZ locations
  - Low-frequency check (every 3 hours)

**Day 5: Condition Service**
- Build the unified condition service:
  - Aggregates data from all sources for a location + date
  - Returns normalized ConditionReport object
  - Handles missing data gracefully (not all locations have tide data)
- Build condition fetching for a list of activities (batch optimization)
- Write tests for condition normalization

### Deliverables
- Weather, tide, and solar data fetchable for any NZ location
- Data cached in Redis with appropriate TTLs
- Unified condition service aggregates all sources
- Condition data normalized to internal schemas

## Week 10: Condition Scoring & Assessment

### Tasks

**Day 1-2: Activity Condition Profiles**
- Implement condition scoring system (from CONDITION-MONITORING.md):
  - Define ConditionProfile for each activity type (hiking, marine, scenic, etc.)
  - Load profiles from the knowledge base
  - Score current conditions against profiles (0-100 scale)
- Map scores to assessment levels: EXCELLENT / GOOD / FAIR / POOR / UNSAFE
- Handle special rules (DOC track closures → UNSAFE override)

**Day 3-4: Condition API Endpoints**
- Build condition endpoints:
  - GET /conditions/current?lat=X&lon=Y
  - GET /conditions/forecast?lat=X&lon=Y&days=5
  - GET /conditions/assess?activity_id=X&date=Y
- Add condition badges to itinerary day cards (green/yellow/red indicators)
- Add condition summary to day detail view

**Day 5: Trip Activation**
- Implement trip activation flow (confirmed → active):
  - Set trip status to "active" when trip start date arrives (or manually)
  - Begin condition monitoring for active trips
  - Start scheduling daily briefing tasks
- Build Celery periodic tasks:
  - Condition refresh task (hourly for active trips)
  - Briefing scheduling task (checks which trips need morning briefings)

### Deliverables
- Activities scored against real condition data
- Condition badges visible on itinerary
- Active trips trigger condition monitoring
- Background tasks running for condition refresh

## Week 11: Daily Briefing

### Tasks

**Day 1-2: Briefing Generation**
- Implement daily briefing generator:
  - Fetch today's itinerary plan
  - Fetch conditions for each activity location
  - Score each activity
  - Generate briefing via AI (using PROMPT-ARCHITECTURE.md briefing prompt)
  - Include: overall assessment, activity cards, timeline, packing list, hidden gem
- Build briefing storage (database table for generated briefings)

**Day 3-4: Briefing UI**
- Build daily briefing screen:
  - Day header with weather summary
  - Overall assessment banner (green/yellow/orange/red)
  - Activity cards with condition indicators
  - Expandable guidance for each activity (packing, tips, timing)
  - Consolidated packing list
  - Day timeline
- Make briefing accessible from:
  - Push notification tap
  - Today tab in navigation
  - Itinerary day detail

**Day 5: Activity Guidance**
- Implement activity guidance generation:
  - Condition-specific packing list
  - Optimal timing with reasoning
  - Pro tips from knowledge base (RAG retrieval)
  - Safety considerations based on today's conditions
  - Photography tips (if user has photography interest)
- Build activity detail expansion UI (bottom sheet with full guidance)

### Deliverables
- Daily briefings generated with real condition data
- Beautiful briefing UI with expandable activity guidance
- Condition-specific packing lists and timing suggestions
- Pro tips and hidden gems from knowledge base

## Week 12: Push Notifications

### Tasks

**Day 1-2: Web Push Setup**
- Implement service worker for PWA push notifications
- Set up VAPID keys for web push
- Build push subscription management (frontend registration → backend storage)
- Implement push notification delivery (pywebpush)
- Handle notification permission request flow

**Day 3-4: Notification Types**
- Implement morning briefing notification:
  - Scheduled based on user's configured time + timezone
  - Brief summary with overall assessment
  - Tap opens full briefing
- Implement evening preview notification:
  - Tomorrow's plan summary
  - Key packing items
- Implement notification preferences UI (timing, categories, quiet hours)

**Day 5: Notification Scheduling**
- Build timezone-aware scheduling:
  - Store user's trip timezone
  - Schedule briefing generation 5 min before configured time
  - Deliver notification at configured time
- Build notification suppression (quiet hours, frequency caps)
- Test full notification flow end-to-end

### Deliverables
- PWA push notifications working end-to-end
- Morning briefing notifications delivered on schedule
- Evening preview notifications
- User-configurable notification timing and preferences

## Week 13: Adaptive Itinerary (Swap Engine)

### Tasks

**Day 1-2: Swap Detection**
- Implement swap opportunity detection (from ITINERARY-ADAPTATION.md):
  - When a day's activity scores FAIR or POOR, check if another day within the trip has better conditions
  - Score the improvement (condition delta)
  - Score the disruption (logistics impact, cascading changes)
  - Apply thresholds: STRONG_SWAP / SUGGEST / MENTION / NO_ACTION
- Build swap evaluation prompt (AI evaluates and generates human-readable explanation)

**Day 3-4: Swap UI**
- Build swap suggestion screen:
  - Clear before/after comparison
  - Condition indicators for both days
  - Reasoning text from AI
  - Logistics impact summary
  - Accept / Decline / Tell Me More buttons
- Implement swap acceptance:
  - Update itinerary (swap the two days)
  - Regenerate affected briefings
  - Confirm to user
- Implement swap decline:
  - Record decline (don't re-suggest)
  - Provide tips for making the best of suboptimal conditions

**Day 5: Swap Notifications**
- Build swap suggestion push notification
- Schedule swap checks (run during evening before, so user has time to plan)
- Limit swap frequency (max 2-3 per trip)
- Test full swap flow end-to-end

### Deliverables
- Swap engine detects improvement opportunities from real condition data
- Swap suggestions presented with clear reasoning
- User can accept (itinerary updates) or decline (tips provided)
- Swap notifications delivered proactively

## Week 14: Live Companion Polish

### Tasks

**Day 1-2: Free-Form Chat During Trip**
- Extend chat agent for live companion mode:
  - Context: current itinerary + today's conditions + user location context
  - Handle questions: "What should I do if it rains?", "Tell me more about this place"
  - Handle changes: "I want to skip today's hike", "Can we add a wine tasting?"
  - Handle logistics: "Where's the nearest gas station?", "What's for dinner?"
- Add chat access from the bottom navigation bar

**Day 3-4: Map Integration**
- Build map view:
  - Full route on Mapbox map
  - Attraction pins color-coded by condition status
  - Current day highlighted
  - Tap pin for activity details
  - Route segments with driving times
- Add "current location" indicator (GPS-based, when app is active)
- Map accessible from bottom navigation

**Day 5: End-to-End Testing**
- Test complete live companion flow:
  - Trip activates → conditions monitored → briefing generated → notification sent
  - Open briefing → see conditions → expand activity guidance → see packing list
  - Swap detected → notification → review → accept/decline
  - Chat with Buddi about today's plan
- Fix bugs and edge cases
- Performance optimization (caching, query optimization)

### Deliverables
- Live chat with Buddi during the trip (context-aware)
- Map view with route and condition-coded attraction pins
- Full live companion experience working end-to-end

## Phase 3 Definition of Done

- [ ] Weather, tide, and solar data integrated and cached
- [ ] Activities scored against real conditions
- [ ] Daily briefings generated with condition-specific guidance
- [ ] Push notifications delivered on schedule
- [ ] Swap engine detects and suggests itinerary improvements
- [ ] User can accept/decline swaps
- [ ] Free-form chat works during trip with context
- [ ] Map shows route with condition-coded pins
- [ ] The experience proves that condition-aware travel planning adds real value
