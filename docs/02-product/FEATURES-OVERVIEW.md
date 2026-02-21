# Features Overview

## Feature Architecture

Journey Buddi's features are organized into two major phases of the user experience, each containing multiple feature groups. This document provides the high-level map — each feature group has its own detailed specification document.

## Phase A: Trip Planning (Pre-Trip)

The planning phase happens before the traveler departs. It transforms the user's interests and preferences into a fully structured, optimized itinerary through AI-guided conversation.

### A1. User Onboarding & Preferences
**Goal:** Understand who the traveler is without asking overwhelming open-ended questions.

- Structured preference collection through concrete choices
- Travel style profiling (pace, adventure level, fitness)
- Interest mapping (wildlife, landscapes, water, culture, food, photography, history)
- Budget range indication
- Trip dates and duration flexibility
- Previous travel experience assessment

### A2. AI-Guided Itinerary Building
**Goal:** Build a complete trip plan through natural, structured conversation with Buddi.

- Destination-specific attraction presentation with comparisons
- Smart attraction placement (best location along route when multiple options exist)
- Route optimization considering geography, drive times, and logical flow
- Pace calibration (activities per day matching user preference)
- Day-by-day itinerary assembly with timing suggestions
- Duration recommendation based on selected activities

### A3. Transport Planning
**Goal:** Recommend optimal transport modes for each segment of the trip with clear reasoning.

- Multi-modal transport analysis (car, motorhome, bus, ferry, domestic flight)
- Segment-by-segment recommendations
- Cost estimates and trade-offs
- Practical logistics (pickup/dropoff locations, ferry bookings, etc.)
- Reasoning transparency ("South Island is best by motorhome because...")

### A4. Itinerary Review & Refinement
**Goal:** Let the user review, understand, and adjust the complete itinerary before departure.

- Visual day-by-day itinerary view with map
- Activity cards with descriptions, conditions needed, and timing
- Drag-and-drop reordering (Buddi validates feasibility)
- Add/remove activities with automatic re-optimization
- Trip summary with stats (total days, driving hours, activity count, etc.)
- Export/share capability

## Phase B: Live Companion (During Trip)

The live companion phase activates once the trip begins. It transforms the static itinerary into an adaptive, condition-aware daily guide.

### B1. Daily Briefing
**Goal:** Each morning, give the traveler a clear picture of the day ahead with condition assessment.

- Today's activity summary with timing
- Weather and condition overview for each activity
- Condition quality score (great / good / fair / poor)
- Packing list for the day based on actual conditions
- Departure time recommendation
- Key tips and preparation notes

### B2. Condition Monitoring
**Goal:** Continuously track environmental conditions relevant to upcoming activities.

- Weather forecasting (temperature, precipitation, cloud cover, wind)
- Tide monitoring (high/low tide times and levels)
- Solar and aurora activity tracking
- Sunrise/sunset and golden hour calculations
- Wildlife activity pattern awareness
- Multi-day lookahead (not just today but next 3-5 days)

### B3. Adaptive Itinerary Management
**Goal:** When conditions significantly impact planned activities, suggest smart swaps.

- Condition-activity compatibility analysis
- Swap suggestion engine with clear reasoning
- Impact assessment ("swapping days 3 and 5 means...")
- Logistics adjustment guidance (driving changes, timing shifts)
- User acceptance/rejection flow
- Threshold calibration (don't suggest changes for minor variations)

### B4. Activity Guidance
**Goal:** For each activity, provide expert-level preparation and in-context guidance.

- Detailed packing list specific to the activity AND today's conditions
- Optimal arrival time with reasoning
- Best viewpoints, photo spots, and hidden gems
- Local stories, history, and interesting facts
- Safety considerations and warnings
- Nearby alternatives if conditions deteriorate during the activity

### B5. Notification System
**Goal:** Proactive, timely, non-intrusive communication with the traveler.

- Morning briefing notification (configurable time)
- Condition alert notifications (significant changes detected)
- Swap suggestion notifications
- Activity preparation reminders (evening before)
- All notifications respect user's quiet hours and preferences

## Cross-Cutting Features

### C1. Chat with Buddi
**Goal:** On-demand conversational access to Buddi for questions, changes, or tips.

- Natural language conversation about the trip
- "What should I do if it rains today?"
- "Tell me more about this attraction"
- "I want to add a wine tasting day"
- Context-aware responses (Buddi knows where you are in the trip)

### C2. Map Integration
**Goal:** Visual representation of the trip with interactive route and attraction display.

- Route visualization on map
- Activity locations with condition indicators
- Current location awareness
- Nearby point-of-interest discovery
- Driving directions and estimated times

### C3. User Account & Persistence
**Goal:** Simple account system for data persistence without auth complexity.

- Magic link (email-based) authentication — no passwords
- Trip data persistence across devices
- Multiple trip support (plan your next trip while on current one)
- Trip history and memories

## Feature Priority Matrix

| Feature | Impact | Complexity | Phase |
|---------|--------|-----------|-------|
| User Preferences | High | Low | MVP |
| AI Itinerary Building | Critical | High | MVP |
| Transport Planning | High | Medium | MVP |
| Itinerary Review | High | Medium | MVP |
| Daily Briefing | Critical | Medium | V1.1 |
| Condition Monitoring | Critical | High | V1.1 |
| Adaptive Itinerary | High | Very High | V1.1 |
| Activity Guidance | High | Medium | V1.1 |
| Notifications | Medium | Medium | V1.1 |
| Chat with Buddi | High | Medium | MVP |
| Map Integration | Medium | Medium | MVP |
| User Account | High | Low | MVP |
