# Development Roadmap — Overview

## Philosophy

Build the smallest thing that proves the core value proposition, then iterate. Journey Buddi's core value is: **AI-guided planning + condition-aware live companion**. The roadmap is structured to deliver that core as quickly as possible, then layer on sophistication.

## Phase Summary

```
Phase 1: Foundation (Weeks 1-3)
  → Project setup, database, auth, basic frontend shell

Phase 2: Planning AI (Weeks 4-8)  
  → The conversational planning experience with Buddi
  → User can chat with AI and get a complete NZ itinerary

Phase 3: Live Companion (Weeks 9-14)
  → Weather integration, condition monitoring, daily briefings
  → The adaptive itinerary with swap suggestions

Phase 4: Polish & Launch (Weeks 15-18)
  → UX polish, testing, performance, soft launch

Phase 5: Growth & Expansion (Ongoing)
  → Mobile app, new destinations, B2B marketplace
```

## What "Done" Looks Like for Each Phase

### Phase 1 Complete
A user can sign up (magic link), see a dashboard, and access a basic chat interface. The backend serves data from PostgreSQL. The project is deployed and accessible online.

### Phase 2 Complete
A user can have a full planning conversation with Buddi about a New Zealand trip. Buddi asks about preferences, presents attractions, builds a route, and generates a day-by-day itinerary. The itinerary is stored and viewable.

### Phase 3 Complete
For an active trip, the user receives daily briefings with real condition data. Buddi suggests swaps when conditions warrant. Activity guidance includes condition-specific packing, timing, and tips.

### Phase 4 Complete
The app is polished, performant, and ready for real users. Landing page communicates the value proposition. End-to-end experience is smooth and delightful.

### Phase 5 (Ongoing)
React Native mobile app. New destinations added. B2B features explored.

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| AI quality too low | Start with Gemini Pro for all tasks; upgrade to GPT-4 for critical paths if needed |
| Weather API costs too high | Start with Open-Meteo (free) + OpenWeatherMap free tier |
| NZ knowledge insufficient | Supplement LLM knowledge with curated knowledge base; validate with personal research |
| Scope creep | Each phase has a strict "done" definition; features defer to next phase if not core |
| Two-person team capacity | Focus ruthlessly; no nice-to-haves until core is proven |

## Success Criteria

### MVP (End of Phase 4)
- 10 test users complete the full planning + companion experience
- AI generates itineraries that feel genuinely useful and smart
- Condition monitoring accurately reflects real weather conditions
- At least 1 swap suggestion correctly identified a better day for an activity
- Users report the experience is meaningfully better than their current planning approach

### Growth (Phase 5+)
- 100+ itineraries created per month
- 70%+ swap suggestion acceptance rate
- Positive user feedback on daily briefing quality
- Ready to add a second destination
